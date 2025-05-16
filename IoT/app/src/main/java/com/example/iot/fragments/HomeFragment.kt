package com.example.iot.fragments

import com.example.iot.R

class HomeFragment : BaseFragment() {
    override fun getLayoutResId(): Int = R.layout.fragment_home
    
    companion object {
        fun newInstance() = HomeFragment()
    }
}