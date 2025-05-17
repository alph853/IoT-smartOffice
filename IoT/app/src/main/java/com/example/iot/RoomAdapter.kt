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

class RoomAdapter(private val rooms: List<Room>) : RecyclerView.Adapter<RoomAdapter.RoomViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RoomViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_room, parent, false)
        return RoomViewHolder(view)
    }

    override fun onBindViewHolder(holder: RoomViewHolder, position: Int) {
        val room = rooms[position]
        holder.tvRoomName.text = room.name
        holder.tvRoomDesc.text = room.description
        holder.tvDeviceCount.text = "${room.deviceCount} active device(s)"
        // Optionally set image if you have different icons

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
        holder.tvRoomDesc.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize)
        holder.tvDeviceCount.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize)

        // Set Room TextView marginTop proportionally to card width (20/190 ratio)
        val roomMarginTop = (cardEdge * 20 / 190).toInt()
        val roomParams = holder.tvRoomName.layoutParams as MarginLayoutParams
        roomParams.topMargin = roomMarginTop
        holder.tvRoomName.layoutParams = roomParams

        // Set Building TextView marginTop proportionally to card width (4/190 ratio)
        val buildingMarginTop = (cardEdge * 4 / 190).toInt()
        val buildingParams = holder.tvRoomDesc.layoutParams as MarginLayoutParams
        buildingParams.topMargin = buildingMarginTop
        holder.tvRoomDesc.layoutParams = buildingParams

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

    override fun getItemCount(): Int = rooms.size

    class RoomViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvRoomName: TextView = itemView.findViewById(R.id.tvRoomName)
        val tvRoomDesc: TextView = itemView.findViewById(R.id.tvRoomDesc)
        val tvDeviceCount: TextView = itemView.findViewById(R.id.tvDeviceCount)
        val imgRoom: ImageView = itemView.findViewById(R.id.imgRoom)
        val cardView: View = itemView.findViewById(R.id.cardView)
        val linearLayout: LinearLayout = itemView.findViewById(R.id.linearLayout)
    }
} 