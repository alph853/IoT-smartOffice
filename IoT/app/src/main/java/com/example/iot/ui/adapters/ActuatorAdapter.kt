package com.example.iot.ui.adapters

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.domain.models.Actuator
import com.example.iot.domain.models.MCU
import com.example.iot.R

class ActuatorAdapter(
    private val actuators: List<Actuator>
) : RecyclerView.Adapter<ActuatorAdapter.ActuatorViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ActuatorViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_actuator, parent, false)
        return ActuatorViewHolder(view)
    }

    override fun onBindViewHolder(holder: ActuatorViewHolder, position: Int) {
        val actuator = actuators[position]
        holder.tvName.text = actuator.name
        holder.tvType.text = actuator.type

        // Set icon based on actuator type
        when (actuator.type.lowercase()) {
            "fan" -> holder.imgIcon.setImageResource(R.drawable.ic_fan)
            "led4rgb" -> holder.imgIcon.setImageResource(R.drawable.ic_led4rgb)
            "indicator", "led", "light" -> holder.imgIcon.setImageResource(R.drawable.ic_bulb)
            "lighting" -> holder.imgIcon.setImageResource(R.drawable.ic_ceiling_light)
            else -> holder.imgIcon.setImageResource(R.drawable.ic_control)
        }
    }

    override fun getItemCount(): Int = actuators.size

    class ActuatorViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val imgIcon: ImageView = itemView.findViewById(R.id.imgActuator)
        val tvName: TextView = itemView.findViewById(R.id.tvActuatorName)
        val tvType: TextView = itemView.findViewById(R.id.tvActuatorType)
    }
}