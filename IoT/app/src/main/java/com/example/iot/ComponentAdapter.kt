package com.example.iot

import android.app.AlertDialog
import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class ComponentAdapter(
    private val components: MutableList<Component>,
    private val context: Context,
    private val onComponentChanged: () -> Unit
) : RecyclerView.Adapter<ComponentAdapter.ComponentViewHolder>() {
    private var removeMode = false
    private var modifyMode = false

    fun setRemoveMode(enabled: Boolean) {
        removeMode = enabled
        if (enabled) modifyMode = false
        notifyDataSetChanged()
    }

    fun setModifyMode(enabled: Boolean) {
        modifyMode = enabled
        if (enabled) removeMode = false
        notifyDataSetChanged()
    }

    fun isRemoveMode() = removeMode
    fun isModifyMode() = modifyMode

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ComponentViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_component, parent, false)
        return ComponentViewHolder(view)
    }

    override fun onBindViewHolder(holder: ComponentViewHolder, position: Int) {
        val component = components[position]
        holder.tvName.text = component.name
        holder.tvType.text = component.type
        // Set icon based on type/name if desired
        // holder.imgIcon.setImageResource(...)

        // Set status dot color
        val statusDot = holder.itemView.findViewById<View>(R.id.viewStatusDot)
        if (component.status) {
            statusDot.setBackgroundResource(R.drawable.bg_status_dot_green)
        } else {
            statusDot.setBackgroundResource(R.drawable.bg_status_dot_red)
        }

        holder.itemView.setOnClickListener {
            when {
                removeMode -> {
                    components.removeAt(position)
                    notifyItemRemoved(position)
                    onComponentChanged()
                }
                modifyMode -> {
                    showEditDialog(holder, component, position)
                }
            }
        }
        // Toggle status on long click
        holder.itemView.setOnLongClickListener {
            component.status = !component.status
            notifyItemChanged(position)
            onComponentChanged()
            true
        }
    }

    override fun getItemCount(): Int = components.size

    private fun showEditDialog(holder: ComponentViewHolder, component: Component, position: Int) {
        val dialogView = LayoutInflater.from(context).inflate(R.layout.dialog_edit, null)
        val editText = dialogView.findViewById<EditText>(R.id.editText)
        editText.setText(component.name)
        val editType = EditText(context)
        editType.setText(component.type)
        editType.hint = "Component Type"
        (dialogView as ViewGroup).addView(editType)

        val dialog = AlertDialog.Builder(context)
            .setTitle("Edit Component")
            .setView(dialogView)
            .create()

        dialogView.findViewById<Button>(R.id.btnConfirm).setOnClickListener {
            val newName = editText.text.toString()
            val newType = editType.text.toString()
            if (newName.isNotEmpty() && newType.isNotEmpty()) {
                component.name = newName
                component.type = newType
                notifyItemChanged(position)
                onComponentChanged()
            }
            dialog.dismiss()
        }
        dialogView.findViewById<Button>(R.id.btnCancel).setOnClickListener {
            dialog.dismiss()
        }
        dialog.show()
    }

    class ComponentViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val imgIcon: ImageView = itemView.findViewById(R.id.imgComponent)
        val tvName: TextView = itemView.findViewById(R.id.tvComponentName)
        val tvType: TextView = itemView.findViewById(R.id.tvComponentType)
    }
} 