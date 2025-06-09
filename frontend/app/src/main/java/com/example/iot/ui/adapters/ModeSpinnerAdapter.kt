package com.example.iot.ui.adapters

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.TextView
import com.example.iot.R

class ModeSpinnerAdapter(
    context: Context,
    private val modes: Array<String>
) : ArrayAdapter<String>(context, R.layout.item_spinner_mode, modes) {

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        return createItemView(position, convertView, parent)
    }

    override fun getDropDownView(position: Int, convertView: View?, parent: ViewGroup): View {
        return createItemView(position, convertView, parent)
    }

    private fun createItemView(position: Int, convertView: View?, parent: ViewGroup): View {
        val view = convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.item_spinner_mode, parent, false)

        // Since our layout is a TextView itself, we can cast the view
        (view as TextView).text = modes[position]

        return view
    }
} 