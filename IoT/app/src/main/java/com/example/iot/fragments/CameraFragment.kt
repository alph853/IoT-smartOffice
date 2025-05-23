package com.example.iot.fragments

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.EditText
import com.example.iot.R

class CameraFragment : BaseFragment() {
    private lateinit var etPrompt: EditText
    
    override fun getLayoutResId(): Int = R.layout.fragment_camera
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        etPrompt = view.findViewById(R.id.et_prompt)
        setupTextChangeListener()
    }
    
    private fun setupTextChangeListener() {
        etPrompt.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {
                // Handle before text changed if needed
            }

            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                // Handle on text changed if needed
            }

            override fun afterTextChanged(s: Editable?) {
                // Handle after text changed if needed
            }
        })
    }
    
    companion object {
        fun newInstance() = CameraFragment()
    }
}