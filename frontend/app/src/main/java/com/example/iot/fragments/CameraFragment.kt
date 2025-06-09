package com.example.iot.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.EditText
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.R
import com.example.iot.domain.repositories.ImageRepository
import com.example.iot.ui.adapters.ImageAdapter
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class CameraFragment : Fragment() {
    private lateinit var etPrompt: EditText
    private lateinit var imageRepository: ImageRepository
    private lateinit var imageAdapter: ImageAdapter
    private lateinit var recyclerView: RecyclerView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_camera, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        etPrompt = view.findViewById(R.id.et_prompt)
        recyclerView = view.findViewById(R.id.rv_images)
        setupSearchListener()
        setupRecyclerView()
        setupRetrofit()
        fetchImages()
    }

    private fun setupRecyclerView() {
        imageAdapter = ImageAdapter()
        recyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = imageAdapter
        }
    }

    private fun setupRetrofit() {
        val retrofit = Retrofit.Builder()
            .baseUrl("https://10diemiot.ngrok.io/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        imageRepository = retrofit.create(ImageRepository::class.java)
    }

    private fun setupSearchListener() {
        etPrompt.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH || actionId == EditorInfo.IME_ACTION_DONE) {
                val query = etPrompt.text.toString()
                if (query.isNotEmpty()) {
                    searchImages(query)
                }
                true
            } else {
                false
            }
        }
    }

    private fun searchImages(query: String) {
        lifecycleScope.launch {
            try {
                val response = imageRepository.searchImages(query)
                imageAdapter.submitList(response.images)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun fetchImages() {
        lifecycleScope.launch {
            try {
                val response = imageRepository.getImages()
                imageAdapter.submitList(response.images)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    companion object {
        fun newInstance() = CameraFragment()
    }
}