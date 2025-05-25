package com.example.iot

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ImageButton
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.widget.PopupMenu

class RoomDetailActivity : AppCompatActivity() {

    private lateinit var navigationBar: NavigationBar
    private lateinit var mcuAdapter: MCUAdapter
    private lateinit var tvActiveCount: TextView
    private var currentRoom: Room? = null

    companion object {
        private const val EXTRA_ROOM_NAME = "extra_room_name"
        private const val EXTRA_ROOM_DESC = "extra_room_desc"
        private const val EXTRA_ROOM_ID = "extra_room_id"

        fun newIntent(context: Context, room: Room, roomID: Int): Intent {
            return Intent(context, RoomDetailActivity::class.java).apply {
                putExtra(EXTRA_ROOM_NAME, room.name)
                putExtra(EXTRA_ROOM_DESC, room.description)
                putExtra(EXTRA_ROOM_ID, roomID)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        supportActionBar?.hide()
        setContentView(R.layout.activity_room_detail)

        // Get room index from intent
        val roomID = intent.getIntExtra(EXTRA_ROOM_ID, -1)
        if (roomID == -1) {
            finish()
            return
        }

        // Get the current room
        currentRoom = RoomManager.getRoomByID(roomID)
        if (currentRoom == null) {
            finish()
            return
        }

        // Apply window insets properly
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.detail_main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            // Only apply left and right padding to the main container
            v.updatePadding(left = systemBars.left, right = systemBars.right)
            insets
        }

        // Setup views
        tvActiveCount = findViewById(R.id.tv_active_count)
        findViewById<TextView>(R.id.tvDetailRoomName).text = currentRoom?.name ?: "Unknown Room"

        setupUI()
    }

    private fun setupUI() {
        // Setup back button
        findViewById<View>(R.id.backButton).setOnClickListener {
            finish()
        }

        // Setup menu button event
        val btnMenu = findViewById<ImageButton>(R.id.btn_menu)
        btnMenu.setOnClickListener { v ->
            val popup = PopupMenu(this, v)
            popup.menu.add(0, 0, 0, "Add")
            popup.menu.add(0, 1, 1, "Remove")
            popup.menu.add(0, 2, 2, "Modify")
            popup.setOnMenuItemClickListener { item ->
                when (item.itemId) {
                    0 -> {
                        onMenuAdd()
                        true
                    }
                    1 -> {
                        onMenuRemove()
                        true
                    }
                    2 -> {
                        onMenuModify()
                        true
                    }
                    else -> false
                }
            }
            popup.show()
        }

        // Setup RecyclerView for MCU cards
        val rvMCUs = findViewById<RecyclerView>(R.id.rvMCUs)
        currentRoom?.let { room ->
            mcuAdapter = MCUAdapter(
                room,
                { updateActiveCount() },
                { mcu -> onMCUCardClicked(mcu) }
            )
            rvMCUs.layoutManager = GridLayoutManager(this, 2)
            rvMCUs.adapter = mcuAdapter
        }

        // Add click listener to root layout to hide remove button
        findViewById<View>(R.id.detail_main).setOnClickListener {
            if (::mcuAdapter.isInitialized) {
                if (mcuAdapter.isRemoveMode()) {
                    mcuAdapter.setRemoveMode(false)
                }
                if (mcuAdapter.isModifyMode()) {
                    mcuAdapter.setModifyMode(false)
                }
            }
        }

        // Update active count initially
        updateActiveCount()

        // Setup navigation bar
        setupNavigationBar()
    }
    override fun onResume() {
        super.onResume()
        // Refresh the adapter to show any updates
        if (::mcuAdapter.isInitialized) {
            mcuAdapter.notifyDataSetChanged()
        }
        updateActiveCount()
    }

    private fun updateActiveCount() {
        tvActiveCount.text = "${currentRoom?.deviceCount ?: 0} MCU(s)"
    }
    
    private fun onMCUCardClicked(mcu: MCU) {
        // Get the room index
        val roomID = currentRoom?.id ?: return
        // Navigate to MCU detail screen
        val intent = MCUDetailActivity.newIntent(this, mcu, roomID)
        startActivity(intent)
    }

    private fun onMenuAdd() {
        currentRoom?.let { room ->
            // Create a new MCU with default values
            val newMCU = MCU()
            room.addMCU(newMCU)
            if (::mcuAdapter.isInitialized) {
                mcuAdapter.notifyItemInserted(room.deviceCount - 1)
            }
            updateActiveCount()
        }
    }

    private fun onMenuRemove() {
        // Toggle remove mode in the adapter
        if (::mcuAdapter.isInitialized) {
            mcuAdapter.setRemoveMode(!mcuAdapter.isRemoveMode())
        }
    }

    private fun onMenuModify() {
        // Toggle modify mode in the adapter
        if (::mcuAdapter.isInitialized) {
            mcuAdapter.setModifyMode(!mcuAdapter.isModifyMode())
        }
    }
    
    private fun setupNavigationBar() {
        navigationBar = NavigationBar(this)
        navigationBar.setup()
        
        // Set the Home tab as selected (index 0) since room details belong to Home functionality
        navigationBar.setSelectedIndex(0)
        
        // Handle navigation item clicks
        navigationBar.setOnItemSelectedListener { index ->
            if (index == 0) {
                // When Home tab is clicked, always go back to MainActivity's home screen
                val intent = Intent(this, MainActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
                startActivity(intent)
                finish()
            } else {
                // For other tabs, start the MainActivity and set the appropriate tab
                val intent = Intent(this, MainActivity::class.java)
                intent.putExtra("selected_tab", index)
                startActivity(intent)
                finish()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up the callback when the activity is destroyed
        MCUDetailActivity.removeOnMCUUpdateListener()
    }
} 