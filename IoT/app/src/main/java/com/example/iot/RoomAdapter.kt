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

class RoomAdapter(
    private val rooms: MutableList<Room>,
    private val onRoomRemoved: () -> Unit,
    private val onRoomClicked: ((Room) -> Unit)? = null
) : RecyclerView.Adapter<RoomAdapter.RoomViewHolder>() {
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

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RoomViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_room, parent, false)
        return RoomViewHolder(view)
    }

    override fun onBindViewHolder(holder: RoomViewHolder, position: Int) {
        val room = rooms[position]
        holder.tvRoomName.text = room.name
        holder.tvRoomBuilding.text = room.building
        holder.tvDeviceCount.text = "${room.deviceCount} active device(s)"

        // Show/hide remove icon based on remove mode
        holder.imgRemove.visibility = if (_isRemoveMode) View.VISIBLE else View.GONE
        // Show/hide edit icon based on modify mode
        holder.imgEdit.visibility = if (_isModifyMode) View.VISIBLE else View.GONE

        // Set click listener for remove button
        holder.imgRemove.setOnClickListener {
            // Remove the room at this position
            RoomManager.removeRoom(position)
            notifyItemRemoved(position)
            // Notify adapter of the range of items that changed
            notifyItemRangeChanged(position, RoomManager.getRoomCount())
            // Notify MainActivity to update active count
            onRoomRemoved()
        }
        
        // Set card click listener if we have a callback
        holder.cardView.setOnClickListener {
            if (!_isRemoveMode && !_isModifyMode) {
                onRoomClicked?.invoke(room)
            }
        }

        // Set click listeners for text modification
        if (_isModifyMode) {
            holder.tvRoomName.setOnClickListener {
                showEditDialog(holder.tvRoomName, position, true)
            }
            holder.tvRoomBuilding.setOnClickListener {
                showEditDialog(holder.tvRoomBuilding, position, false)
            }
        } else {
            holder.tvRoomName.setOnClickListener(null)
            holder.tvRoomBuilding.setOnClickListener(null)
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
        val imageParams = holder.imgRoom.layoutParams
        imageParams.width = imageSize
        imageParams.height = imageSize
        holder.imgRoom.layoutParams = imageParams

        // Set text size proportionally to card width (12/190 ratio)
        val textSize = (cardEdge * 12 / 190).toFloat()
        holder.tvRoomName.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize)
        holder.tvRoomBuilding.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize)
        holder.tvDeviceCount.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize)

        // Set Room TextView marginTop proportionally to card width (20/190 ratio)
        val roomMarginTop = (cardEdge * 20 / 190).toInt()
        val roomParams = holder.tvRoomName.layoutParams as MarginLayoutParams
        roomParams.topMargin = roomMarginTop
        holder.tvRoomName.layoutParams = roomParams

        // Set Building TextView marginTop proportionally to card width (4/190 ratio)
        val buildingMarginTop = (cardEdge * 4 / 190).toInt()
        val buildingParams = holder.tvRoomBuilding.layoutParams as MarginLayoutParams
        buildingParams.topMargin = buildingMarginTop
        holder.tvRoomBuilding.layoutParams = buildingParams

        // Set device count TextView marginTop proportionally to card width (10/190 ratio)
        val deviceMarginTop = (cardEdge * 10 / 190).toInt()
        val deviceParams = holder.tvDeviceCount.layoutParams as MarginLayoutParams
        deviceParams.topMargin = deviceMarginTop
        holder.tvDeviceCount.layoutParams = deviceParams

        // Set device count TextView padding left and right proportionally to card width (22/190 ratio)
        val devicePadding = (cardEdge * 22 / 190).toInt()
        val devicePaddingTopBot = (cardEdge * 6 / 190).toInt()
        holder.tvDeviceCount.setPadding(
            devicePadding,
            devicePaddingTopBot,
            devicePadding,
            devicePaddingTopBot
        )
    }

    private fun showEditDialog(textView: TextView, position: Int, isRoomName: Boolean) {
        val context = textView.context
        val dialogView = LayoutInflater.from(context).inflate(R.layout.dialog_edit, null)
        val editText = dialogView.findViewById<EditText>(R.id.editText)
        editText.setText(textView.text)
        
        val dialog = AlertDialog.Builder(context)
            .setTitle(if (isRoomName) "Edit Room Name" else "Edit Building")
            .setView(dialogView)
            .create()
        
        dialogView.findViewById<Button>(R.id.btnConfirm).setOnClickListener {
            val newText = editText.text.toString()
            if (newText.isNotEmpty()) {
                textView.text = newText
                if (isRoomName) {
                    rooms[position].name = newText
                } else {
                    rooms[position].description = newText
                }
            }
            dialog.dismiss()
        }
        
        dialogView.findViewById<Button>(R.id.btnCancel).setOnClickListener {
            dialog.dismiss()
        }
        
        dialog.show()
    }

    override fun getItemCount(): Int = rooms.size

    class RoomViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvRoomName: TextView = itemView.findViewById(R.id.tvRoomName)
        val tvRoomBuilding: TextView = itemView.findViewById(R.id.tvRoomBuilding)
        val tvDeviceCount: TextView = itemView.findViewById(R.id.tvDeviceCount)
        val imgRoom: ImageView = itemView.findViewById(R.id.imgRoom)
        val imgRemove: ImageButton = itemView.findViewById(R.id.imgRemove)
        val imgEdit: ImageButton = itemView.findViewById(R.id.imgEdit)
        val cardView: View = itemView.findViewById(R.id.cardView)
        val linearLayout: LinearLayout = itemView.findViewById(R.id.linearLayout)
    }
} 