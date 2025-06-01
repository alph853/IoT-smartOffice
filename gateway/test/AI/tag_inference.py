import torch.nn.functional as F
import torch
import numpy as np
from PIL import Image
from models import ram_plus, get_transform
import os

class TagInference:
    def __init__(self,
                 weight_path='ram_plus_swin_large_14m.pth',
                 image_size=384,
                 vit='swin_l',
                 device='cuda',
                 ):

        weight_path = os.path.join(os.path.dirname(__file__), "models", "weights", weight_path)
        self.transform = get_transform(image_size=image_size)
        self.model = ram_plus(pretrained=weight_path,
                              image_size=image_size,
                              vit=vit)
        self.device = device if device == 'cuda' and torch.cuda.is_available() else 'cpu'

        self.model.eval()
        self.model = self.model.to(self.device)

    def inference(self, image_paths: list[str], batch_size=16):
        tag_outputs = []
        tag_logits = []
        batches = [image_paths[i:i+batch_size] for i in range(0, len(image_paths), batch_size)]

        for batch in batches:
            transformed_images = [self._transform_image(p) for p in batch]
            images_batch = torch.cat(transformed_images).to(self.device)
            tag_output, tag_logit = self._generate_tag(images_batch)
            tag_outputs.extend(tag_output)
            tag_logits.extend(tag_logit)

        tag_contexts = []
        for b in range(len(tag_outputs)):
            tag_context = []
            tag_output, tag_logit = tag_outputs[b], tag_logits[b]
            tag_frequency = np.round(tag_logit*10).astype(int)
            for tag, freq in zip(tag_output, tag_frequency):
                tag_context.extend([tag]*freq)
            tag_context = ' '.join(map(str, tag_context))
            tag_contexts.append(tag_context)

        return tag_outputs, tag_contexts

    @torch.no_grad()
    def _generate_tag(self, image):
        image_embeds = self.model.image_proj(self.model.visual_encoder(image))
        image_atts = torch.ones(image_embeds.size()[:-1],
                                dtype=torch.long).to(image.device)

        image_cls_embeds = image_embeds[:, 0, :]
        image_spatial_embeds = image_embeds[:, 1:, :]

        bs = image_spatial_embeds.shape[0]

        des_per_class = int(self.model.label_embed.shape[0] / self.model.num_class)

        image_cls_embeds = image_cls_embeds / image_cls_embeds.norm(dim=-1, keepdim=True)
        reweight_scale = self.model.reweight_scale.exp()
        logits_per_image = (reweight_scale * image_cls_embeds @ self.model.label_embed.t())
        logits_per_image = logits_per_image.view(bs, -1, des_per_class)

        weight_normalized = F.softmax(logits_per_image, dim=2)
        label_embed_reweight = torch.empty(bs, self.model.num_class, 512).to(image.device).to(image.dtype)

        for i in range(bs):
            reshaped_value = self.model.label_embed.view(-1, des_per_class, 512)
            product = weight_normalized[i].unsqueeze(-1) * reshaped_value
            label_embed_reweight[i] = product.sum(dim=1)

        label_embed = torch.nn.functional.relu(self.model.wordvec_proj(label_embed_reweight))

        # recognized image tags using alignment decoder
        tagging_embed = self.model.tagging_head(
            encoder_embeds=label_embed,
            encoder_hidden_states=image_embeds,
            encoder_attention_mask=image_atts,
            return_dict=False,
            mode='tagging',
        )

        logits = torch.sigmoid(self.model.fc(tagging_embed[0]).squeeze(-1))

        targets = torch.where(
            logits > self.model.class_threshold.to(image.device),
            torch.tensor(1.0).to(image.device),
            torch.zeros(self.model.num_class).to(image.device))

        tag = targets.cpu().numpy()
        tag[:, self.model.delete_tag_index] = 0
        tag_outputs = []
        tag_logits = []

        for b in range(bs):
            index = np.argwhere(tag[b] == 1)

            tokens = self.model.tag_list[index].squeeze(axis=1)
            tag_outputs.append([token.replace(" ", "_") for token in tokens])

            score = logits[b][index[:, 0]].cpu().numpy()
            tag_logits.append(score)

        return tag_outputs, tag_logits

    def _transform_image(self, image_path):
        return self.transform(Image.open(image_path)).unsqueeze(0).to(self.device)

