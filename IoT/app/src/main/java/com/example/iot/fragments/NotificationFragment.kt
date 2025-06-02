package com.example.iot.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.ItemTouchHelper
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

import com.example.iot.fragments.ControlFragment
import com.example.iot.domain.managers.NotificationManager
import com.example.iot.NotificationDetailActivity
import android.content.Intent

import com.google.android.material.tabs.TabLayout
import com.example.iot.data.viewmodels.Notification
import com.example.iot.data.viewmodels.NotificationViewModel
import com.example.iot.data.viewmodels.NotificationFilter
import com.example.iot.ui.adapters.NotificationAdapter
import com.example.iot.R
import okhttp3.*
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

class NotificationFragment : Fragment() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: NotificationAdapter
    private lateinit var tabFilter: TabLayout
    private lateinit var btnMarkAllRead: Button
    private lateinit var btnMarkAllUnread: Button
    private lateinit var btnDeleteAll: Button
    private val viewModel: NotificationViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_notification, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupHeader(view)
        setupFilters(view)
        setupRecyclerView(view)
        setupBulkActions(view)
        loadNotifications()
    }

    private fun setupHeader(view: View) {
        view.findViewById<TextView>(R.id.header_title)?.text = getString(R.string.notification)
        view.findViewById<TextView>(R.id.header_subtitle)?.visibility = View.GONE
        view.findViewById<View>(R.id.profile_icon)?.visibility = View.GONE
    }

    private fun setupFilters(view: View) {
        tabFilter = view.findViewById(R.id.tab_filter)
        tabFilter.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                val filter = when (tab?.position) {
                    1 -> NotificationFilter.READ
                    2 -> NotificationFilter.UNREAD
                    else -> NotificationFilter.ALL
                }
                viewModel.setFilter(filter)
            }
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
    }

    private fun setupRecyclerView(view: View) {
        recyclerView = view.findViewById(R.id.recycler_notifications)
        adapter = NotificationAdapter(
            onItemClick = { notification ->
                // Mark as read via REST API, then update UI and navigate
                android.util.Log.d("NotificationFragment", "onItemClick: ${notification.id}")
                val client = OkHttpClient()
                val request = Request.Builder()
                    .url("https://10diemiot.ngrok.io/notifications/mark-as-read/${notification.id}")
                    .patch(ByteArray(0).toRequestBody())
                    .build()
                client.newCall(request).enqueue(object : Callback {
                    override fun onFailure(call: Call, e: IOException) {
                        requireActivity().runOnUiThread {
                            android.widget.Toast.makeText(requireContext(), "Failed to mark as read: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
                        }
                    }
                    override fun onResponse(call: Call, response: Response) {
                        requireActivity().runOnUiThread {
                            if (response.isSuccessful) {
                                viewModel.toggleRead(notification)
                                // Navigate to detail activity
                                val intent = NotificationDetailActivity.newIntent(requireContext(), notification)
                                startActivity(intent)
                            } else {
                                android.widget.Toast.makeText(requireContext(), "Failed to mark as read", android.widget.Toast.LENGTH_SHORT).show()
                            }
                        }
                    }
                })
            },
            onItemSwiped = { notification -> viewModel.deleteNotification(notification) }
        )
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = adapter
        val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(0, ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT) {
            override fun onMove(rv: RecyclerView, vh: RecyclerView.ViewHolder, target: RecyclerView.ViewHolder) = false
            override fun onSwiped(vh: RecyclerView.ViewHolder, dir: Int) {
                val notification = adapter.currentList[vh.adapterPosition]
                viewModel.deleteNotification(notification)
            }
        })
        itemTouchHelper.attachToRecyclerView(recyclerView)
        recyclerView.itemAnimator?.changeDuration = 100
        recyclerView.itemAnimator?.moveDuration = 100
        recyclerView.itemAnimator?.addDuration = 100
        recyclerView.itemAnimator?.removeDuration = 100
        viewModel.filteredNotifications.observe(viewLifecycleOwner) { adapter.submitList(it) }
    }

    private fun setupBulkActions(view: View) {
        btnMarkAllRead = view.findViewById(R.id.btn_mark_all_read)
//        btnMarkAllUnread = view.findViewById(R.id.btn_mark_all_unread)
        btnDeleteAll = view.findViewById(R.id.btn_delete_all)
        btnMarkAllRead.setOnClickListener {
            val client = OkHttpClient()
            val request = Request.Builder()
                .url("https://10diemiot.ngrok.io/notifications/mark-all-as-read")
                .patch(ByteArray(0).toRequestBody())
                .build()
            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    requireActivity().runOnUiThread {
                        android.widget.Toast.makeText(requireContext(), "Failed to mark all as read: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onResponse(call: Call, response: Response) {
                    requireActivity().runOnUiThread {
                        if (response.isSuccessful) {
                            viewModel.markAllRead()
                            android.widget.Toast.makeText(requireContext(), "Marked all as read", android.widget.Toast.LENGTH_SHORT).show()
                        } else {
                            android.widget.Toast.makeText(requireContext(), "Failed to mark all as read", android.widget.Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            })
        }
//        btnMarkAllUnread.setOnClickListener {
//            val client = OkHttpClient()
//            val request = Request.Builder()
//                .url("https://10diemiot.ngrok.io/notifications/mark-all-as-unread")
//                .post(RequestBody.create(null, ByteArray(0)))
//                .build()
//            client.newCall(request).enqueue(object : Callback {
//                override fun onFailure(call: Call, e: IOException) {
//                    requireActivity().runOnUiThread {
//                        android.widget.Toast.makeText(requireContext(), "Failed to mark all as unread: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
//                    }
//                }
//                override fun onResponse(call: Call, response: Response) {
//                    requireActivity().runOnUiThread {
//                        if (response.isSuccessful) {
//                            viewModel.markAllUnread()
//                            android.widget.Toast.makeText(requireContext(), "Marked all as unread", android.widget.Toast.LENGTH_SHORT).show()
//                        } else {
//                            android.widget.Toast.makeText(requireContext(), "Failed to mark all as unread", android.widget.Toast.LENGTH_SHORT).show()
//                        }
//                    }
//                }
//            })
//        }
        btnDeleteAll.setOnClickListener {
            val client = OkHttpClient()
            val request = Request.Builder()
                .url("https://10diemiot.ngrok.io/notifications")
                .delete()
                .build()
            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    requireActivity().runOnUiThread {
                        android.widget.Toast.makeText(requireContext(), "Failed to delete all notifications: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onResponse(call: Call, response: Response) {
                    requireActivity().runOnUiThread {
                        if (response.isSuccessful) {
                            viewModel.deleteAll()
                            android.widget.Toast.makeText(requireContext(), "Deleted all notifications", android.widget.Toast.LENGTH_SHORT).show()
                        } else {
                            android.widget.Toast.makeText(requireContext(), "Failed to delete all notifications", android.widget.Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            })
        }
    }

    private fun loadNotifications() {
        // Load real notifications from NotificationManager
        viewModel.loadNotifications()
        
        // If no notifications are available, load sample data for testing
//        if (NotificationManager.getNotificationCount() == 0) {
//            viewModel.loadSampleNotifications()
//        }
    }

    override fun onResume() {
        super.onResume()
        // Refresh notifications when returning to this fragment
        loadNotifications()
    }

    companion object {
        fun newInstance() = NotificationFragment()
    }
}