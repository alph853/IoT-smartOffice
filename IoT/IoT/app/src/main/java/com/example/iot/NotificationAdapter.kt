package com.example.iot

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

class NotificationAdapter(
    private val onItemClick: (Notification) -> Unit,
    private val onItemLongClick: (Notification) -> Unit,
    private val onItemSwiped: (Notification) -> Unit
) : ListAdapter<Notification, NotificationAdapter.NotificationViewHolder>(NotificationDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): NotificationViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_notification, parent, false)
        return NotificationViewHolder(view)
    }

    override fun onBindViewHolder(holder: NotificationViewHolder, position: Int) {
        val notification = getItem(position)
        holder.bind(notification)
        holder.itemView.setOnClickListener { onItemClick(notification) }
        holder.itemView.setOnLongClickListener {
            onItemLongClick(notification)
            true
        }
    }

    inner class NotificationViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val icon: ImageView = itemView.findViewById(R.id.notification_icon)
        private val title: TextView = itemView.findViewById(R.id.notification_title)
        private val summary: TextView = itemView.findViewById(R.id.notification_summary)
        private val time: TextView = itemView.findViewById(R.id.notification_time)
        private val indicator: View = itemView.findViewById(R.id.indicator)

        fun bind(notification: Notification) {
            icon.setImageResource(notification.iconRes)
            title.text = notification.title
            summary.text = notification.summary
            time.text = notification.time
            if (!notification.isRead) {
                indicator.visibility = View.VISIBLE
                indicator.setBackgroundResource(R.drawable.indicator_unread)
            } else {
                indicator.visibility = View.INVISIBLE
            }
            // Optional: giảm opacity nếu đã đọc
            itemView.alpha = if (notification.isRead) 0.6f else 1.0f
        }
    }
}

class NotificationDiffCallback : DiffUtil.ItemCallback<Notification>() {
    override fun areItemsTheSame(oldItem: Notification, newItem: Notification): Boolean = oldItem.id == newItem.id
    override fun areContentsTheSame(oldItem: Notification, newItem: Notification): Boolean = oldItem == newItem
} 