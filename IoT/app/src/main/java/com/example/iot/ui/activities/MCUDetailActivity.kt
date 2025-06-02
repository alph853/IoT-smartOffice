package com.example.iot.ui.activities

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding
import android.app.AlertDialog
import android.widget.EditText
import android.widget.Button
import android.widget.ImageButton
import android.widget.PopupMenu
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.domain.models.MCU
import com.example.iot.domain.models.Room
import com.example.iot.domain.models.MCUUpdateRequest
import com.example.iot.domain.managers.RoomManager
import com.example.iot.ui.adapters.SensorAdapter
import com.example.iot.ui.adapters.ActuatorAdapter
import com.example.iot.ui.navigation.NavigationBar
import com.example.iot.ui.activities.MainActivity
import com.example.iot.R
import okhttp3.*
import java.io.IOException
import com.google.gson.Gson
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody

class MCUDetailActivity : AppCompatActivity() {

    private lateinit var navigationBar: NavigationBar
    private lateinit var mcu: MCU
    private lateinit var originalMCU: MCU
    private lateinit var currentRoom: Room
    private lateinit var sensorAdapter: SensorAdapter
    private lateinit var actuatorAdapter: ActuatorAdapter

    companion object {
        private const val EXTRA_MCU_ID = "extra_mcu_id"
        private const val EXTRA_MCU_NAME = "extra_mcu_name"
        private const val EXTRA_MCU_STATUS = "extra_mcu_status"
        private const val EXTRA_MCU_DESCRIPTION = "extra_mcu_description"
        private const val EXTRA_MCU_LOCATION = "extra_mcu_location"
        private const val EXTRA_MCU_REGISTER_AT = "extra_mcu_register_at"
        private const val EXTRA_MCU_MAC_ADDRESS = "extra_mcu_mac_address"
        private const val EXTRA_MCU_FIRMWARE_VERSION = "extra_mcu_firmware_version"
        private const val EXTRA_MCU_LAST_SEEN_AS = "extra_mcu_last_seen_as"
        private const val EXTRA_MCU_MODEL = "extra_mcu_model"
        private const val EXTRA_ROOM_ID = "extra_room_id"

        // Static callback field to handle MCU updates
        private var onMCUUpdateListener: ((MCU) -> Unit)? = null

        // Method to set the callback
        fun setOnMCUUpdateListener(listener: (MCU) -> Unit) {
            onMCUUpdateListener = listener
        }

        // Method to remove the callback
        fun removeOnMCUUpdateListener() {
            onMCUUpdateListener = null
        }

        fun newIntent(context: Context, mcu: MCU, roomID: Int): Intent {
            return Intent(context, MCUDetailActivity::class.java).apply {
                putExtra(EXTRA_MCU_ID, mcu.id)
                putExtra(EXTRA_MCU_NAME, mcu.name)
                putExtra(EXTRA_MCU_STATUS, mcu.status)
                putExtra(EXTRA_MCU_DESCRIPTION, mcu.description)
                putExtra(EXTRA_MCU_LOCATION, mcu.location)
                putExtra(EXTRA_MCU_REGISTER_AT, mcu.registered_at)
                putExtra(EXTRA_MCU_MAC_ADDRESS, mcu.mac_addr)
                putExtra(EXTRA_MCU_FIRMWARE_VERSION, mcu.fw_version)
                putExtra(EXTRA_MCU_LAST_SEEN_AS, mcu.last_seen_at)
                putExtra(EXTRA_MCU_MODEL, mcu.model)
                putExtra(EXTRA_ROOM_ID, roomID)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        supportActionBar?.hide()
        setContentView(R.layout.activity_mcu_detail)

        // Apply window insets properly
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.mcu_detail_main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.updatePadding(left = systemBars.left, right = systemBars.right)
            insets
        }

        // Get room index from intent
        val roomID = intent.getIntExtra(EXTRA_ROOM_ID, -1)
        if (roomID == -1) {
            finish()
            return
        }

        // Get the current room
        currentRoom = RoomManager.getRoomByID(roomID) ?: run {
            finish()
            return
        }

        // Get MCU ID from intent
        val mcuId = intent.getIntExtra(EXTRA_MCU_ID, -1)

        // Try to get the existing MCU from the room using ID
        val existingMCU = if (mcuId != -1) {
            currentRoom.getMCUs().find { it.id == mcuId }
        } else null

        if (existingMCU != null) {
            // Use the existing MCU if found
            mcu = existingMCU.copy()
            originalMCU = existingMCU
        } else {
            // Create a new MCU if not found
            mcu = MCU()
            originalMCU = mcu.copy()
        }

        // Set MCU name in the header
        findViewById<TextView>(R.id.tvDetailMCUName).text = mcu.name

        // Setup back button
        findViewById<View>(R.id.backButton).setOnClickListener {
            finish()
        }

        // Setup navigation bar
        setupNavigationBar()

        // Setup all clickable items
        setupClickableItems()

        // Display MCU information
        displayMCUInfo()

        // Setup sensor and actuator RecyclerViews
        setupSensorAndActuatorSections()
    }

    private fun setupClickableItems() {
        // MCU Info section
        findViewById<View>(R.id.nameLayout).setOnClickListener {
            showEditDialog("Name", mcu.name) { newValue ->
                mcu.name = newValue
                findViewById<TextView>(R.id.tvName).text = newValue
                findViewById<TextView>(R.id.tvDetailMCUName).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.descriptionLayout).setOnClickListener {
            showEditDialog("Description", mcu.description) { newValue ->
                mcu.description = newValue
                findViewById<TextView>(R.id.tvDescription).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.locationLayout).setOnClickListener {
            showEditDialog("Location", mcu.location) { newValue ->
                mcu.location = newValue
                findViewById<TextView>(R.id.tvLocation).text = newValue
                saveMCUChanges()
            }
        }

        // Technical Info section
        findViewById<View>(R.id.registerAtLayout).setOnClickListener {
            showEditDialog("Register at", mcu.registered_at) { newValue ->
                mcu.registered_at = newValue
                findViewById<TextView>(R.id.tvRegisterAt).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.macAddressLayout).setOnClickListener {
            showEditDialog("Mac address", mcu.mac_addr) { newValue ->
                mcu.mac_addr = newValue
                findViewById<TextView>(R.id.tvMacAddress).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.firmwareVersionLayout).setOnClickListener {
            showEditDialog("Firmware version", mcu.fw_version) { newValue ->
                mcu.fw_version = newValue
                findViewById<TextView>(R.id.tvFirmwareVersion).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.lastSeenLayout).setOnClickListener {
            showEditDialog("Last seen at", mcu.last_seen_at) { newValue ->
                mcu.last_seen_at = newValue
                findViewById<TextView>(R.id.tvLastSeenAs).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.modelLayout).setOnClickListener {
            showEditDialog("Model", mcu.model) { newValue ->
                mcu.model = newValue
                findViewById<TextView>(R.id.tvModel).text = newValue
                saveMCUChanges()
            }
        }
    }

    private fun displayMCUInfo() {
        findViewById<TextView>(R.id.tvName).text = mcu.name
        findViewById<TextView>(R.id.tvDescription).text = mcu.description
        findViewById<TextView>(R.id.tvLocation).text = mcu.location
        findViewById<TextView>(R.id.tvRegisterAt).text = mcu.registered_at
        findViewById<TextView>(R.id.tvMacAddress).text = mcu.mac_addr
        findViewById<TextView>(R.id.tvFirmwareVersion).text = mcu.fw_version
        findViewById<TextView>(R.id.tvLastSeenAs).text = mcu.last_seen_at
        findViewById<TextView>(R.id.tvModel).text = mcu.model
    }

    private fun showEditDialog(title: String, currentValue: String, onConfirm: (String) -> Unit) {
        val dialog = AlertDialog.Builder(this, R.style.CustomAlertDialog)
            .create()

        val dialogView = layoutInflater.inflate(R.layout.dialog_edit, null)
        val editText = dialogView.findViewById<EditText>(R.id.editText)
        editText.setText(currentValue)

        // Set up confirm button
        dialogView.findViewById<Button>(R.id.btnConfirm).setOnClickListener {
            val newValue = editText.text.toString()
            if (newValue.isNotEmpty()) {
                onConfirm(newValue)
            }
            dialog.dismiss()
        }

        // Set up cancel button
        dialogView.findViewById<Button>(R.id.btnCancel).setOnClickListener {
            dialog.dismiss()
        }

        dialog.setTitle(title)
        dialog.setView(dialogView)
        dialog.show()
    }

    private fun saveMCUChanges() {
        currentRoom.updateMCU(originalMCU, mcu)
        originalMCU = mcu.copy() // Update the original MCU reference

        // --- REST API call to update MCU ---
        val client = OkHttpClient()
        val gson = Gson()

        // Create the update request
        val updateRequest = MCUUpdateRequest(
            name = mcu.name,
            description = mcu.description,
            fw_version = mcu.fw_version,
            model = mcu.model,
            office_id = mcu.office_id,
            gateway_id = mcu.gateway_id,
            status = mcu.status,
            access_token = mcu.access_token,
            last_seen_at = mcu.last_seen_at,
            actuators = mcu.actuators,
            sensors = mcu.sensors
        )

        val mcuJson = gson.toJson(updateRequest)
        val url = "https://10diemiot.ngrok.io/devices/${mcu.id}"
        val body = mcuJson.toRequestBody("application/json".toMediaTypeOrNull())
        val request = Request.Builder().url(url).patch(body).build()
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    android.widget.Toast.makeText(this@MCUDetailActivity, "Failed to update MCU: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
                }
            }
            override fun onResponse(call: Call, response: Response) {
                runOnUiThread {
                    if (response.isSuccessful) {
                        android.widget.Toast.makeText(this@MCUDetailActivity, "MCU updated successfully", android.widget.Toast.LENGTH_SHORT).show()
                    } else {
                        android.widget.Toast.makeText(this@MCUDetailActivity, "Failed to update MCU", android.widget.Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    private fun setupNavigationBar() {
        navigationBar = NavigationBar(this)
        navigationBar.setup()

        // Set the Home tab as selected (index 0) since MCU details belong to Home functionality
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

    private fun setupSensorAndActuatorSections() {
        // Setup Sensors RecyclerView
        val rvSensors = findViewById<RecyclerView>(R.id.rvSensors)
        sensorAdapter = SensorAdapter(mcu.sensors)
        rvSensors.layoutManager = LinearLayoutManager(this)
        rvSensors.adapter = sensorAdapter

        // Setup Actuators RecyclerView
        val rvActuators = findViewById<RecyclerView>(R.id.rvActuators)
        actuatorAdapter = ActuatorAdapter(mcu.actuators)
        rvActuators.layoutManager = LinearLayoutManager(this)
        rvActuators.adapter = actuatorAdapter
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up the callback when the activity is destroyed
        removeOnMCUUpdateListener()
    }
} 