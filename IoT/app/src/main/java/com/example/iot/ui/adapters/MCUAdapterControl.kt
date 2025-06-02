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

class MCUAdapterControl(
    private val mcus: List<MCU>,
    private val onMcuToggled: (MCU, Boolean) -> Unit
) : RecyclerView.Adapter<MCUAdapterControl.McuViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): McuViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_mcu_control, parent, false)
        return McuViewHolder(view)
    }

    override fun onBindViewHolder(holder: McuViewHolder, position: Int) {
        val mcu = mcus[position]
        holder.bind(mcu)
    }

    override fun getItemCount(): Int = mcus.size

    inner class McuViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val imgIcon: ImageView = itemView.findViewById(R.id.imgMCU)
        private val tvName: TextView = itemView.findViewById(R.id.tvMCUName)
        private val tvDesc: TextView = itemView.findViewById(R.id.tvMCUDesc)
        private val tvStatus: TextView = itemView.findViewById(R.id.tvStatus)
        private val cardView: View = itemView.findViewById(R.id.cardView)

        fun bind(mcu: MCU) {
            tvName.text = mcu.name
            tvDesc.text = mcu.description
            tvStatus.text = mcu.status
            
            // Set status text color based on online/offline status
            if (mcu.status.equals("Online", ignoreCase = true)) {
                tvStatus.setTextColor(itemView.context.getColor(R.color.green))
            } else {
                tvStatus.setTextColor(itemView.context.getColor(R.color.red))
            }

            // Set click listener for the card
            cardView.setOnClickListener {
                val isCurrentlyOnline = mcu.status.equals("Online", ignoreCase = true)
                onMcuToggled(mcu, !isCurrentlyOnline)
            }
        }
    }
} 