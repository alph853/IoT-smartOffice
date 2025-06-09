package com.example.iot.ui.adapters

import android.content.res.Resources
import android.util.TypedValue
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import android.widget.LinearLayout
import androidx.recyclerview.widget.RecyclerView
import android.view.ViewGroup.MarginLayoutParams
import android.widget.ImageButton
import android.app.AlertDialog
import android.widget.EditText
import android.widget.Button
import android.content.Context
import androidx.core.content.ContextCompat
import com.example.iot.domain.models.MCU
import com.example.iot.domain.models.Room
import com.example.iot.domain.models.Component
import com.example.iot.R
import com.google.android.material.switchmaterial.SwitchMaterial

class MCUAdapter(
    private val room: Room,
    private val onMCURemoved: () -> Unit,
    private val onMCUClicked: ((MCU) -> Unit)? = null
) : RecyclerView.Adapter<MCUAdapter.MCUViewHolder>() {
    // A reference to any view context we can use for dialogs
    private var viewContext: Context? = null
    
    private var _isRemoveMode = false
    private var _isModifyMode = false

    fun getMCUs(): List<MCU> = room.getMCUs()

    fun setRemoveMode(enabled: Boolean) {
        _isRemoveMode = enabled
        _isModifyMode = false // Disable modify mode when remove mode is enabled
        notifyDataSetChanged()
    }

    fun setModifyMode(enabled: Boolean) {
        _isModifyMode = enabled
        _isRemoveMode = false // Disable remove mode when modify mode is enabled
        notifyDataSetChanged()
    }

    fun isRemoveMode(): Boolean = _isRemoveMode
    fun isModifyMode(): Boolean = _isModifyMode

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MCUViewHolder {
        // Store the context for later use
        viewContext = parent.context
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_mcu, parent, false)
        return MCUViewHolder(view)
    }

    override fun onBindViewHolder(holder: MCUViewHolder, position: Int) {
        val mcu = room.getMCUs()[position]
        holder.tvMCUName.text = mcu.name
        holder.tvMCUDesc.text = mcu.description
        holder.tvStatus.text = mcu.status
        
        // Store the context for dialog use
        viewContext = holder.itemView.context
        
        // Set status background color based on online/offline status
        if (mcu.status.equals("Online", ignoreCase = true)) {
            holder.tvStatus.setTextColor(ContextCompat.getColor(holder.itemView.context, R.color.green))
        } else {
            holder.tvStatus.setTextColor(ContextCompat.getColor(holder.itemView.context, R.color.red))
        }

        // Show/hide remove icon based on remove mode
        holder.imgRemove.visibility = if (_isRemoveMode) View.VISIBLE else View.GONE
        // Show/hide edit icon based on modify mode
        holder.imgEdit.visibility = if (_isModifyMode) View.VISIBLE else View.GONE

        // Set click listener for remove button
        holder.imgRemove.setOnClickListener {
            // Remove the MCU at this position
            room.removeMCU(mcu)
            notifyItemRemoved(position)
            // Notify adapter of the range of items that changed
            notifyItemRangeChanged(position, room.deviceCount)
            // Notify RoomDetailActivity to update active count
            onMCURemoved()
        }
        
        // Set card click listener if we have a callback
        holder.cardView.setOnClickListener {
            if (!_isRemoveMode && !_isModifyMode) {
                onMCUClicked?.invoke(mcu)
            }
        }

        // Set click listeners for text modification
        if (_isModifyMode) {
            holder.tvMCUName.setOnClickListener {
                showEditDialog(holder.tvMCUName, mcu, "name")
            }
            holder.tvMCUDesc.setOnClickListener {
                showEditDialog(holder.tvMCUDesc, mcu, "description")
            }
        } else {
            holder.tvMCUName.setOnClickListener(null)
            holder.tvMCUDesc.setOnClickListener(null)
        }

        // Set card size to be square: edge = (device width - 60dp) / 2
        val displayMetrics = Resources.getSystem().displayMetrics
        val marginDp = 60f
        val marginPx = TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, marginDp, displayMetrics).toInt()
        val cardEdge = (displayMetrics.widthPixels - marginPx) / 2
        val params = holder.cardView.layoutParams
        params.width = cardEdge
        params.height = cardEdge
        holder.cardView.layoutParams = params

        // Set LinearLayout paddingTop proportionally to card width (20/190 ratio)
        val paddingStart = (cardEdge * 20 / 190).toInt()
        val paddingEnd = (cardEdge * 20 / 190).toInt()
        val paddingTop = (cardEdge * 20 / 190).toInt()
        val paddingBot = (cardEdge * 14 / 190).toInt()
        holder.linearLayout.setPadding(
            paddingStart,
            paddingTop,
            paddingEnd,
            paddingBot
        )

        // Set ImageView size proportionally to card width (64/190 ratio)
        val imageSize = (cardEdge * 64 / 190).toInt()
        val imageParams = holder.imgMCU.layoutParams
        imageParams.width = imageSize
        imageParams.height = imageSize
        holder.imgMCU.layoutParams = imageParams

        // Set text size proportionally to card width (12/190 ratio)
        val textSize = (cardEdge * 12 / 190).toFloat()
        holder.tvMCUName.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize)
        holder.tvMCUDesc.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize)
        holder.tvStatus.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize * 10 / 12)

        // Set MCU TextView marginTop proportionally to card width (20/190 ratio)
        val mcuMarginTop = (cardEdge * 20 / 190).toInt()
        val mcuParams = holder.tvMCUName.layoutParams as MarginLayoutParams
        mcuParams.topMargin = mcuMarginTop
        holder.tvMCUName.layoutParams = mcuParams

        // Set Device TextView marginTop proportionally to card width (4/190 ratio)
        val deviceMarginTop = (cardEdge * 4 / 190).toInt()
        val deviceParams = holder.tvMCUDesc.layoutParams as MarginLayoutParams
        deviceParams.topMargin = deviceMarginTop
        holder.tvMCUDesc.layoutParams = deviceParams
        
//        // Set LinearLayout for mode/status marginTop proportionally to card width (12/190 ratio)
//        val statusLinearLayoutMarginBottom = 0
//        val statusLinearParams = holder.statusLinearLayout.layoutParams as MarginLayoutParams
//        statusLinearParams.bottomMargin = statusLinearLayoutMarginBottom
//        holder.statusLinearLayout.layoutParams = statusLinearParams

//        // Set LinearLayout paddingTop proportionally to card width (20/190 ratio)
//        val paddingStartEnd = (cardEdge * 20 / 190).toInt()
//        holder.statusLinearLayout.setPadding(
//            paddingStartEnd,
//            0,
//            paddingStartEnd,
//            0
//        )

    }

    private fun showEditDialog(textView: TextView, mcu: MCU, field: String) {
        val context = textView.context
        val dialogView = LayoutInflater.from(context).inflate(R.layout.dialog_edit, null)
        val editText = dialogView.findViewById<EditText>(R.id.editText)
        editText.setText(textView.text)
        
        val title = when(field) {
            "name" -> "Edit MCU Name"
            "description" -> "Edit Device Type"
            else -> "Edit Text"
        }
        
        val dialog = AlertDialog.Builder(context)
            .setTitle(title)
            .setView(dialogView)
            .create()
        
        dialogView.findViewById<Button>(R.id.btnConfirm).setOnClickListener {
            val newText = editText.text.toString()
            if (newText.isNotEmpty()) {
                // Create updated MCU with new value
                val updatedMCU = mcu.copy(
                    name = if (field == "name") newText else mcu.name,
                    description = if (field == "description") newText else mcu.description
                )
                // Update the MCU in the room
                room.updateMCU(mcu, updatedMCU)
                // Update the view
                textView.text = newText
                // Find position by MCU ID and notify the specific item change
                val position = room.getMCUs().indexOfFirst { it.id == mcu.id }
                if (position != -1) {
                    notifyItemChanged(position)
                }
            }
            dialog.dismiss()
        }
        
        dialogView.findViewById<Button>(R.id.btnCancel).setOnClickListener {
            dialog.dismiss()
        }
        
        dialog.show()
    }

    private fun showStatusDialog(position: Int) {
        // Use the stored context or return if null
        val context = viewContext ?: return
        
        val statuses = arrayOf("Online", "Offline")
        
        val dialog = AlertDialog.Builder(context)
            .setTitle("Select Status")
            .setItems(statuses) { dialog, which ->
                val selectedStatus = statuses[which]
                room.getMCUs()[position].status = selectedStatus
                notifyItemChanged(position)
                dialog.dismiss()
            }
            .create()
            
        dialog.show()
    }

    override fun getItemCount(): Int = room.deviceCount

    class MCUViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvMCUName: TextView = itemView.findViewById(R.id.tvMCUName)
        val tvMCUDesc: TextView = itemView.findViewById(R.id.tvMCUDesc)
        val tvStatus: TextView = itemView.findViewById(R.id.tvStatus)
        val imgMCU: ImageView = itemView.findViewById(R.id.imgMCU)
        val imgRemove: ImageButton = itemView.findViewById(R.id.imgRemove)
        val imgEdit: ImageButton = itemView.findViewById(R.id.imgEdit)
        val cardView: View = itemView.findViewById(R.id.cardView)
        val linearLayout: LinearLayout = itemView.findViewById(R.id.linearLayout)
        val statusLinearLayout: LinearLayout = itemView.findViewById(R.id.statusLinearLayout)
    }
} 