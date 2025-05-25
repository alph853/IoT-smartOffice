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
import com.example.iot.domain.models.MCU
import com.example.iot.domain.models.Sensor
import com.example.iot.R

class SensorAdapter(
    private val sensors: List<Sensor>
) : RecyclerView.Adapter<SensorAdapter.SensorViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SensorViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_sensor, parent, false)
        return SensorViewHolder(view)
    }

    override fun onBindViewHolder(holder: SensorViewHolder, position: Int) {
        val sensor = sensors[position]
        holder.tvName.text = sensor.name
        holder.tvType.text = sensor.type

        // Set icon based on sensor type
        when (sensor.type.lowercase()) {
            "dht20" -> holder.imgIcon.setImageResource(R.drawable.ic_temperature)
            "ldr" -> holder.imgIcon.setImageResource(R.drawable.ic_light_sensor)
            "temperature", "temperature & humidity" -> holder.imgIcon.setImageResource(R.drawable.ic_temperature)
            "humidity" -> holder.imgIcon.setImageResource(R.drawable.ic_humidity)
            "luminosity", "light" -> holder.imgIcon.setImageResource(R.drawable.ic_light_sensor)
            "digital input", "button" -> holder.imgIcon.setImageResource(R.drawable.ic_control)
            else -> holder.imgIcon.setImageResource(R.drawable.ic_climate)
        }
    }

    override fun getItemCount(): Int = sensors.size

    class SensorViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val imgIcon: ImageView = itemView.findViewById(R.id.imgSensor)
        val tvName: TextView = itemView.findViewById(R.id.tvSensorName)
        val tvType: TextView = itemView.findViewById(R.id.tvSensorType)
    }
}