package com.example.iot.ui.adapters

import android.content.res.Resources
import android.graphics.Color
import android.util.TypedValue
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.data.viewmodels.Notification
import com.example.iot.R

class NotificationAdapter(
    private val onItemClick: (Notification) -> Unit,
    private val onItemSwiped: (Notification) -> Unit
) : ListAdapter<Notification, NotificationAdapter.NotificationViewHolder>(NotificationDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): NotificationViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_notification, parent, false)
        return NotificationViewHolder(view)
    }

    override fun onBindViewHolder(holder: NotificationViewHolder, position: Int) {
        val notification = getItem(position)
        holder.bind(notification)
        holder.itemView.setOnClickListener {
            // Immediately update alpha if notification was unread
            if (!notification.read_status) {
                holder.itemView.alpha = 0.6f
            }
            onItemClick(notification)
        }
        
        // Apply dynamic sizing
        holder.applyDynamicSizing()
    }

    inner class NotificationViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val icon: ImageView = itemView.findViewById(R.id.notification_icon)
        private val title: TextView = itemView.findViewById(R.id.notification_title)
        private val summary: TextView = itemView.findViewById(R.id.notification_summary)
        private val time: TextView = itemView.findViewById(R.id.notification_time)
//        private val indicator: View = itemView.findViewById(R.id.indicator)
        private val container: ConstraintLayout = itemView as ConstraintLayout

        fun bind(notification: Notification) {
            icon.setImageResource(notification.iconRes)
            title.text = notification.title
            summary.text = notification.message
            time.text = notification.ts
//            if (!notification.read_status) {
//                indicator.visibility = View.VISIBLE
//                indicator.setBackgroundResource(R.drawable.indicator_unread)
//            } else {
//                indicator.visibility = View.INVISIBLE
//            }
            // Optional: giảm opacity nếu đã đọc
            itemView.alpha = if (notification.read_status) 0.6f else 1.0f
        }

        fun applyDynamicSizing() {
            val displayMetrics = Resources.getSystem().displayMetrics
            val cardWidth = displayMetrics.widthPixels.toFloat()
            
            // Calculate sizes based on card width
            val padding = (cardWidth * 13 / 440).toInt()
            val iconSize = (cardWidth * 40 / 440).toInt()
            val titleTextSize = cardWidth * 16 / 440
            val titleMargin = (cardWidth * 13 / 440).toInt()
            val timeTextSize = cardWidth * 12 / 440
            val indicatorSize = (cardWidth * 14 / 440).toInt()
            val summaryWidth = (cardWidth * 300 / 440).toInt()
            val summaryMarginStart = (cardWidth * 13 / 440).toInt()
            val summaryMarginTop = (cardWidth * 4 / 440).toInt()
            val summaryTextSize = cardWidth * 14 / 440

            // Apply padding to container
            container.setPadding(padding, padding, padding, padding)

            // Apply icon size
            val iconParams = icon.layoutParams
            iconParams.width = iconSize
            iconParams.height = iconSize
            icon.layoutParams = iconParams

            // Apply title text size and margins
            title.setTextSize(TypedValue.COMPLEX_UNIT_PX, titleTextSize)
            val titleParams = title.layoutParams as ConstraintLayout.LayoutParams
            titleParams.marginStart = titleMargin
            titleParams.marginEnd = titleMargin
            title.layoutParams = titleParams

            // Apply time text size
            time.setTextSize(TypedValue.COMPLEX_UNIT_PX, timeTextSize)

            // Apply indicator size
//            val indicatorParams = indicator.layoutParams
//            indicatorParams.width = indicatorSize
//            indicatorParams.height = indicatorSize
//            indicator.layoutParams = indicatorParams

            // Apply summary size and margins
            summary.setTextSize(TypedValue.COMPLEX_UNIT_PX, summaryTextSize)
            val summaryParams = summary.layoutParams as ConstraintLayout.LayoutParams
            summaryParams.width = summaryWidth
            summaryParams.marginStart = summaryMarginStart
            summaryParams.topMargin = summaryMarginTop
            summary.layoutParams = summaryParams
        }
    }
}

class NotificationDiffCallback : DiffUtil.ItemCallback<Notification>() {
    override fun areItemsTheSame(oldItem: Notification, newItem: Notification): Boolean = oldItem.id == newItem.id
    override fun areContentsTheSame(oldItem: Notification, newItem: Notification): Boolean = oldItem == newItem
} 