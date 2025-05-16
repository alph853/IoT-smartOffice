package com.example.iot.fragments

import com.example.iot.R

class NotificationFragment : BaseFragment() {
    override fun getLayoutResId(): Int = R.layout.fragment_notification
    
    companion object {
        fun newInstance() = NotificationFragment()
    }
} 