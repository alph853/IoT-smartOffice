package com.example.iot

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

class MCUDetailActivity : AppCompatActivity() {

    private lateinit var navigationBar: NavigationBar
    private lateinit var mcu: MCU
    private lateinit var originalMCU: MCU
    private lateinit var currentRoom: Room
    private lateinit var componentAdapter: ComponentAdapter

    companion object {
        private const val EXTRA_MCU_ID = "extra_mcu_id"
        private const val EXTRA_MCU_NAME = "extra_mcu_name"
        private const val EXTRA_MCU_STATUS = "extra_mcu_status"
        private const val EXTRA_MCU_DESCRIPTION = "extra_mcu_description"
        private const val EXTRA_MCU_MODE = "extra_mcu_mode"
        private const val EXTRA_MCU_LOCATION = "extra_mcu_location"
        private const val EXTRA_MCU_REGISTER_AT = "extra_mcu_register_at"
        private const val EXTRA_MCU_MAC_ADDRESS = "extra_mcu_mac_address"
        private const val EXTRA_MCU_FIRMWARE_VERSION = "extra_mcu_firmware_version"
        private const val EXTRA_MCU_LAST_SEEN_AS = "extra_mcu_last_seen_as"
        private const val EXTRA_MCU_MODEL = "extra_mcu_model"
        private const val EXTRA_ROOM_INDEX = "extra_room_index"

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

        fun newIntent(context: Context, mcu: MCU, roomIndex: Int): Intent {
            return Intent(context, MCUDetailActivity::class.java).apply {
                putExtra(EXTRA_MCU_ID, mcu.id)
                putExtra(EXTRA_MCU_NAME, mcu.name)
                putExtra(EXTRA_MCU_STATUS, mcu.status)
                putExtra(EXTRA_MCU_DESCRIPTION, mcu.description)
                putExtra(EXTRA_MCU_LOCATION, mcu.location)
                putExtra(EXTRA_MCU_REGISTER_AT, mcu.registerAt)
                putExtra(EXTRA_MCU_MAC_ADDRESS, mcu.macAddress)
                putExtra(EXTRA_MCU_FIRMWARE_VERSION, mcu.firmwareVersion)
                putExtra(EXTRA_MCU_LAST_SEEN_AS, mcu.lastSeenAs)
                putExtra(EXTRA_MCU_MODEL, mcu.model)
                putExtra(EXTRA_ROOM_INDEX, roomIndex)
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
        val roomIndex = intent.getIntExtra(EXTRA_ROOM_INDEX, -1)
        if (roomIndex == -1) {
            finish()
            return
        }

        // Get the current room
        currentRoom = RoomManager.getRooms()[roomIndex]

        // Get MCU ID from intent
        val mcuId = intent.getStringExtra(EXTRA_MCU_ID)
        
        // Try to get the existing MCU from the room using ID
        val existingMCU = if (mcuId != null) {
            currentRoom.getMCUs().find { it.id == mcuId }
        } else null
        
        if (existingMCU != null) {
            // Use the existing MCU if found
            mcu = existingMCU.copy()
            originalMCU = existingMCU
        } else {
            // Create new MCU with values from intent and preserve the ID if it exists
            mcu = MCU(
                id = mcuId ?: java.util.UUID.randomUUID().toString(),
                name = intent.getStringExtra(EXTRA_MCU_NAME) ?: "New MCU",
                status = intent.getStringExtra(EXTRA_MCU_STATUS) ?: "Offline",
                description = intent.getStringExtra(EXTRA_MCU_DESCRIPTION) ?: "New Device",
                location = intent.getStringExtra(EXTRA_MCU_LOCATION) ?: "Not set",
                registerAt = intent.getStringExtra(EXTRA_MCU_REGISTER_AT) ?: "Not registered",
                macAddress = intent.getStringExtra(EXTRA_MCU_MAC_ADDRESS) ?: "Not set",
                firmwareVersion = intent.getStringExtra(EXTRA_MCU_FIRMWARE_VERSION) ?: "1.0.0",
                lastSeenAs = intent.getStringExtra(EXTRA_MCU_LAST_SEEN_AS) ?: "Never",
                model = intent.getStringExtra(EXTRA_MCU_MODEL) ?: "Default Model"
            )
            currentRoom.addMCU(mcu)
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

        // Setup component RecyclerView and menu
        setupComponentSection()
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
            showEditDialog("Register at", mcu.registerAt) { newValue ->
                mcu.registerAt = newValue
                findViewById<TextView>(R.id.tvRegisterAt).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.macAddressLayout).setOnClickListener {
            showEditDialog("Mac address", mcu.macAddress) { newValue ->
                mcu.macAddress = newValue
                findViewById<TextView>(R.id.tvMacAddress).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.firmwareVersionLayout).setOnClickListener {
            showEditDialog("Firmware version", mcu.firmwareVersion) { newValue ->
                mcu.firmwareVersion = newValue
                findViewById<TextView>(R.id.tvFirmwareVersion).text = newValue
                saveMCUChanges()
            }
        }

        findViewById<View>(R.id.lastSeenLayout).setOnClickListener {
            showEditDialog("Last seen as", mcu.lastSeenAs) { newValue ->
                mcu.lastSeenAs = newValue
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
        findViewById<TextView>(R.id.tvRegisterAt).text = mcu.registerAt
        findViewById<TextView>(R.id.tvMacAddress).text = mcu.macAddress
        findViewById<TextView>(R.id.tvFirmwareVersion).text = mcu.firmwareVersion
        findViewById<TextView>(R.id.tvLastSeenAs).text = mcu.lastSeenAs
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

    private fun setupComponentSection() {
        val rvComponents = findViewById<RecyclerView>(R.id.rvComponents)
        componentAdapter = ComponentAdapter(mcu.components, this) {
            saveMCUChanges()
        }
        rvComponents.layoutManager = LinearLayoutManager(this)
        rvComponents.adapter = componentAdapter

        val btnMenu = findViewById<ImageButton>(R.id.btnComponentMenu)
        btnMenu.setOnClickListener { v ->
            val popup = PopupMenu(this, v)
            popup.menu.add(0, 0, 0, "Add")
            popup.menu.add(0, 1, 1, "Remove")
            popup.menu.add(0, 2, 2, "Modify")
            popup.setOnMenuItemClickListener { item ->
                when (item.itemId) {
                    0 -> { // Add
                        mcu.components.add(Component())
                        componentAdapter.notifyItemInserted(mcu.components.size - 1)
                        saveMCUChanges()
                        true
                    }
                    1 -> { // Remove
                        componentAdapter.setRemoveMode(!componentAdapter.isRemoveMode())
                        true
                    }
                    2 -> { // Modify
                        componentAdapter.setModifyMode(!componentAdapter.isModifyMode())
                        true
                    }
                    else -> false
                }
            }
            popup.show()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up the callback when the activity is destroyed
        removeOnMCUUpdateListener()
    }
} 