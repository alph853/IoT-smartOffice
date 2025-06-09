package com.example.iot.fragments

import com.example.iot.R

class SettingFragment : BaseFragment() {
    override fun getLayoutResId(): Int = R.layout.fragment_setting
    
    companion object {
        fun newInstance() = SettingFragment()
    }
} 