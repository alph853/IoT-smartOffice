package com.example.iot.fragments

import com.example.iot.R

class CameraFragment : BaseFragment() {
    override fun getLayoutResId(): Int = R.layout.fragment_camera
    
    companion object {
        fun newInstance() = CameraFragment()
    }
}