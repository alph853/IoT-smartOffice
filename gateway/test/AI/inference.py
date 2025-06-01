import json
import argparse
import sys
from tag_inference import TagInference
from clip_inference import ClipInference


class Inference:
    def __init__(self,
                 device='cuda',
                 contexts=["tag", "clip"]
                 ):
        self.tag_inference = None
        self.clip_inference = None
        if "tag" in contexts:
            self.tag_inference = TagInference(device=device)
        if "clip" in contexts:
            self.clip_inference = ClipInference(device=device)

    def inference(self, image_paths: list[str]):
        res = {}
        if self.tag_inference is not None:
            tag_results = self.tag_inference.inference(image_paths=image_paths)
            res["tag"] = tag_results
        if self.clip_inference is not None:
            clip_results = self.clip_inference.inference(image_paths=image_paths)
            res["clip"] = clip_results

        return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_paths", nargs="+", default=["images"])
    parser.add_argument("--contexts", nargs="+", default=["tag", "clip"])
    parser.add_argument("--device", type=str, default="cuda")

    args = parser.parse_args()

    inference = Inference(contexts=args.contexts, device=args.device,)
    results = inference.inference(image_paths=args.image_paths)

    sys.stdout.write(json.dumps(results))
    sys.stdout.flush()
