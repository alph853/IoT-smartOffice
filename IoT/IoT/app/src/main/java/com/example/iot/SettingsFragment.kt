package com.example.iot

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import android.widget.Toast

class SettingsFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View? {
        Toast.makeText(requireContext(), "Settings feature will be implemented", Toast.LENGTH_SHORT).show()
        return inflater.inflate(R.layout.fragment_home, container, false)
    }
} 