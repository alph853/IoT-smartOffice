package com.example.iot

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


class MCUAdapter(
    private val mcus: MutableList<MCU>,
    private val onMCURemoved: () -> Unit,
    private val onMCUClicked: ((MCU) -> Unit)? = null
) : RecyclerView.Adapter<MCUAdapter.MCUViewHolder>() {
    // A reference to any view context we can use for dialogs
    private var viewContext: Context? = null
    
    private var _isRemoveMode = false
    private var _isModifyMode = false

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
        val mcu = mcus[position]
        holder.tvMCUName.text = mcu.name
        holder.tvMCUDesc.text = mcu.description
        holder.tvMode.text = mcu.mode
        holder.tvStatus.text = mcu.status
        
        // Store the context for dialog use
        viewContext = holder.itemView.context
        
        // Set status background color based on online/offline status
        if (mcu.status.equals("Online", ignoreCase = true)) {
            // Keep the default active badge color
            holder.tvStatus.setTextColor(ContextCompat.getColor(holder.itemView.context, R.color.green))
        } else {
            // Set a different color for offline status (darker or red tint)
            holder.tvStatus.setTextColor(ContextCompat.getColor(holder.itemView.context, R.color.red))
        }

        // Show/hide remove icon based on remove mode
        holder.imgRemove.visibility = if (_isRemoveMode) View.VISIBLE else View.GONE
        // Show/hide edit icon based on modify mode
        holder.imgEdit.visibility = if (_isModifyMode) View.VISIBLE else View.GONE

        // Set click listener for remove button
        holder.imgRemove.setOnClickListener {
            // Remove the MCU at this position
            MCUManager.removeMCU(position)
            notifyItemRemoved(position)
            // Notify adapter of the range of items that changed
            notifyItemRangeChanged(position, MCUManager.getMCUCount())
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
                showEditDialog(holder.tvMCUName, position, "name")
            }
            holder.tvMCUDesc.setOnClickListener {
                showEditDialog(holder.tvMCUDesc, position, "description")
            }
            holder.tvMode.setOnClickListener {
                showModeDialog(position)
            }
            holder.tvStatus.setOnClickListener {
                showStatusDialog(position)
            }
        } else {
            holder.tvMCUName.setOnClickListener(null)
            holder.tvMCUDesc.setOnClickListener(null)
            holder.tvMode.setOnClickListener(null)
            holder.tvStatus.setOnClickListener(null)
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
        val paddingTop = (cardEdge * 20 / 190).toInt()
        val paddingBot = (cardEdge * 14 / 190).toInt()
        holder.linearLayout.setPadding(
            0,
            paddingTop,
            0,
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
        holder.tvMode.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize * 10 / 12)
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
        
        // Set LinearLayout for mode/status marginTop proportionally to card width (12/190 ratio)
        val statusLinearLayoutMarginTop = (cardEdge * 12 / 190).toInt()
        val statusLinearParams = holder.statusLinearLayout.layoutParams as MarginLayoutParams
        statusLinearParams.topMargin = statusLinearLayoutMarginTop
        holder.statusLinearLayout.layoutParams = statusLinearParams

        // Set LinearLayout paddingTop proportionally to card width (20/190 ratio)
        val paddingStartEnd = (cardEdge * 20 / 190).toInt()
        holder.statusLinearLayout.setPadding(
            paddingStartEnd,
            0,
            paddingStartEnd,
            0
        )

    }

    private fun showEditDialog(textView: TextView, position: Int, field: String) {
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
                textView.text = newText
                when(field) {
                    "name" -> mcus[position].name = newText
                    "description" -> mcus[position].description = newText
                }
            }
            dialog.dismiss()
        }
        
        dialogView.findViewById<Button>(R.id.btnCancel).setOnClickListener {
            dialog.dismiss()
        }
        
        dialog.show()
    }
    
    private fun showModeDialog(position: Int) {
        // Use the stored context or return if null
        val context = viewContext ?: return
        
        val modes = arrayOf("Manual", "Schedule", "Auto", "Remote")
        
        val dialog = AlertDialog.Builder(context)
            .setTitle("Select Mode")
            .setItems(modes) { dialog, which ->
                val selectedMode = modes[which]
                mcus[position].mode = selectedMode
                notifyItemChanged(position)
                dialog.dismiss()
            }
            .create()
            
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
                mcus[position].status = selectedStatus
                notifyItemChanged(position)
                dialog.dismiss()
            }
            .create()
            
        dialog.show()
    }

    override fun getItemCount(): Int = mcus.size

    class MCUViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvMCUName: TextView = itemView.findViewById(R.id.tvMCUName)
        val tvMCUDesc: TextView = itemView.findViewById(R.id.tvMCUDesc)
        val tvMode: TextView = itemView.findViewById(R.id.tvMode)
        val tvStatus: TextView = itemView.findViewById(R.id.tvStatus)
        val imgMCU: ImageView = itemView.findViewById(R.id.imgMCU)
        val imgRemove: ImageButton = itemView.findViewById(R.id.imgRemove)
        val imgEdit: ImageButton = itemView.findViewById(R.id.imgEdit)
        val cardView: View = itemView.findViewById(R.id.cardView)
        val linearLayout: LinearLayout = itemView.findViewById(R.id.linearLayout)
        val statusLinearLayout: LinearLayout = itemView.findViewById(R.id.statusLinearLayout)
    }
} 