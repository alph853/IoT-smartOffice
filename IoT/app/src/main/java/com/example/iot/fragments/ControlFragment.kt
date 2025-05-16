package com.example.iot.fragments

import com.example.iot.R

class ControlFragment : BaseFragment() {
    override fun getLayoutResId(): Int = R.layout.fragment_control
    
    companion object {
        fun newInstance() = ControlFragment()
    }
} 