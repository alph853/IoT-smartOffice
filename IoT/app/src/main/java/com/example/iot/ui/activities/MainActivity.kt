package com.example.iot.ui.activities

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.FrameLayout
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding
import com.example.iot.fragments.*
import android.widget.ImageButton
import android.widget.PopupMenu
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.content.Intent
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.InputStreamReader
import java.net.URL
import javax.net.ssl.HttpsURLConnection
import com.example.iot.domain.models.Room
import com.example.iot.domain.managers.RoomManager
import com.example.iot.ui.adapters.RoomAdapter
import com.example.iot.ui.navigation.NavigationBar
import com.example.iot.fragments.NotificationFragment
import com.example.iot.fragments.ControlFragment
import com.example.iot.fragments.CameraFragment
import com.example.iot.fragments.SettingFragment
import com.example.iot.domain.managers.SensorManager
import com.example.iot.domain.managers.ActuatorManager
import com.example.iot.R

class MainActivity : AppCompatActivity() {

    private lateinit var navigationBar: NavigationBar
    private lateinit var homeScreen: ConstraintLayout
    private lateinit var fragmentContainer: FrameLayout
    private lateinit var roomAdapter: RoomAdapter
    private lateinit var tvActiveCount: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        supportActionBar?.hide()
        setContentView(R.layout.activity_main)

        fetchRoomData().start()
        Log.d("onCreate", "Started fetchRoomData")

        // Apply window insets properly
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            // Only apply left and right padding to the main container
            v.updatePadding(left = systemBars.left, right = systemBars.right)
            insets
        }

        // Get references to home screen and fragment container
        homeScreen = findViewById(R.id.home_screen)
        fragmentContainer = findViewById(R.id.fragment_container) ?: FrameLayout(this)
        tvActiveCount = findViewById(R.id.tv_active_count)

        // Setup navigation bar
        navigationBar = NavigationBar(this)
        navigationBar.setup()
        navigationBar.setOnItemSelectedListener { index ->
            showContent(index)
        }

        // Ensure Home UI is visible at startup
        homeScreen.visibility = View.VISIBLE

        // Get selected tab from intent (if any)
        val selectedTab = intent.getIntExtra("selected_tab", 0)

        // Select the appropriate tab
        navigationBar.setSelectedIndex(selectedTab)
        showContent(selectedTab)

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

        // Setup RecyclerView for room cards
        val rvRooms = findViewById<RecyclerView>(R.id.rvRooms)
        roomAdapter = RoomAdapter(
            RoomManager.getRooms(),
            { updateActiveCount() },
            { room -> onRoomCardClicked(room) }
        )
        rvRooms.layoutManager = GridLayoutManager(this, 2)
        rvRooms.adapter = roomAdapter

        // Add click listener to root layout to hide remove button
        findViewById<View>(R.id.main).setOnClickListener {
            if (roomAdapter.isRemoveMode()) {
                roomAdapter.setRemoveMode(false)
            }
            if (roomAdapter.isModifyMode()) {
                roomAdapter.setModifyMode(false)
            }
        }

        // Update active count initially
        updateActiveCount()
    }

    private fun fetchRoomData(): Thread {
        return Thread {
            try {
                val url = URL("https://10diemiot.ngrok.io/office/?return_components=true")
                val conn = url.openConnection() as HttpsURLConnection

                if(conn.responseCode == 200) {
                    val inputStream = conn.inputStream
                    val reader = InputStreamReader(inputStream)
                    val json = reader.readText()
                    Log.d("fetchRoomData", json)

                    // Parse JSON and create Room objects
                    val gson = Gson()
                    val roomListType = object : TypeToken<List<Room>>() {}.type
                    val rooms: List<Room> = gson.fromJson(json, roomListType)

                    // Clear existing rooms and add new ones
                    runOnUiThread {
                        RoomManager.getRooms().clear()
                        SensorManager.getSensors().clear()
                        ActuatorManager.getActuators().clear()

                        rooms.forEach { room ->
                            RoomManager.addRoom(room)
                            Log.d("fetchRoomData", "Added room: ${room.name} (ID: ${room.id}, Building: ${room.building}, Room: ${room.room})")
                            Log.d("fetchRoomData", "  - Devices: ${room.devices.size}")

                            // Log device details
                            room.devices.forEach { device ->
                                // Set location programmatically using format: O{office_id}-{building}-{room}
                                device.location = "O${device.office_id}-${room.building}-${room.room}"
                                
                                Log.d("fetchRoomData", "    Device: ${device.name} (ID: ${device.id}, Status: ${device.status}, Location: ${device.location})")
                                Log.d("fetchRoomData", "      - Sensors: ${device.sensors.size}, Actuators: ${device.actuators.size}")

                                // Add sensors to SensorManager
                                device.sensors.forEach { sensor ->
                                    SensorManager.addSensor(sensor)
                                    Log.d("fetchRoomData", "        Sensor: ${sensor.name} (${sensor.type})")
                                }

                                // Add actuators to ActuatorManager
                                device.actuators.forEach { actuator ->
                                    ActuatorManager.addActuator(actuator)
                                    Log.d("fetchRoomData", "        Actuator: ${actuator.name} (${actuator.type})")
                                }
                            }
                        }
                        Log.d("fetchRoomData", "Total rooms loaded: ${RoomManager.getRoomCount()}")
                        Log.d("fetchRoomData", "Total sensors loaded: ${SensorManager.getSensorCount()}")
                        Log.d("fetchRoomData", "Total actuators loaded: ${ActuatorManager.getActuatorCount()}")
                    }

                    reader.close()
                    inputStream.close()
                    updateUI()
                }
                else {
                    runOnUiThread {
                        tvActiveCount.text = "Connection error"
                        Log.e("fetchRoomData", "HTTP Error: ${conn.responseCode}")
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    tvActiveCount.text = "Network error"
                    Log.e("fetchRoomData", "Exception: ${e.message}", e)
                }
            }
        }
    }

    private fun updateUI() {
        runOnUiThread {
            roomAdapter.notifyDataSetChanged()
            updateActiveCount()
        }
    }

    override fun onResume() {
        super.onResume()
        // Refresh the room list
        roomAdapter.notifyDataSetChanged()
        updateActiveCount()
    }

    private fun onRoomCardClicked(room: Room) {
        // Launch the RoomDetailActivity with room information and index
        val intent = RoomDetailActivity.newIntent(this, room, room.id)
        startActivity(intent)
    }

    private fun updateActiveCount() {
        tvActiveCount.text = "${RoomManager.getRoomCount()} active(s)"
    }

    private fun showContent(index: Int) {
        if (index == 0) {
            // Show Home screen with header
            homeScreen.visibility = View.VISIBLE
            fragmentContainer.visibility = View.GONE
        } else {
            // Show other fragments
            homeScreen.visibility = View.GONE
            fragmentContainer.visibility = View.VISIBLE

            val fragment = when(index) {
                1 -> ControlFragment.newInstance()
                2 -> CameraFragment.newInstance()
                3 -> NotificationFragment.newInstance()
                4 -> SettingFragment.newInstance()
                else -> ControlFragment.newInstance()
            }

            // Replace the fragment
            supportFragmentManager.beginTransaction()
                .replace(R.id.fragment_container, fragment)
                .commit()
        }
    }

    private fun onMenuAdd() {
        // Add a new room card and update the adapter
        RoomManager.addRoom(Room())
        roomAdapter.notifyItemInserted(RoomManager.getRoomCount() - 1)
        updateActiveCount()
    }

    private fun onMenuRemove() {
        // Toggle remove mode in the adapter
        roomAdapter.setRemoveMode(!roomAdapter.isRemoveMode())
    }

    private fun onMenuModify() {
        // Toggle modify mode in the adapter
        roomAdapter.setModifyMode(!roomAdapter.isModifyMode())
    }

    // Handle when this activity resumes (e.g., when returning from other activities)
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)

        // If coming back via HOME tab (no specific tab selected in intent)
        if (!intent.hasExtra("selected_tab")) {
            // Ensure we're showing the home screen and the home tab is selected
            navigationBar.setSelectedIndex(0)
            showContent(0)
            // Update the room list
            roomAdapter.notifyDataSetChanged()
        }
    }
}