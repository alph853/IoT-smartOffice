package com.example.iot.domain.managers

import android.util.Log
import com.example.iot.data.viewmodels.Notification
import com.example.iot.domain.models.MCU
import com.google.gson.Gson
import com.google.gson.JsonObject
import okhttp3.*
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.TimeUnit
import com.example.iot.R

object WebSocketManager {
    private const val TAG = "WebSocketManager"
    private const val WS_URL = "ws://10diemiot.ngrok.io"
    
    private var webSocket: WebSocket? = null
    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS) // Disable timeouts for WebSocket
        .build()
    
    private val gson = Gson()
    
    // Callbacks for UI updates
    private var onDeviceUpdateCallback: (() -> Unit)? = null
    private var onNotificationUpdateCallback: (() -> Unit)? = null
    
    // Buffer for early notifications before UI is ready
    private val earlyNotificationBuffer = mutableListOf<String>()
    private var isUIReady = false
    
    fun setUIReady() {
        isUIReady = true
        // Process any buffered notifications
        if (earlyNotificationBuffer.isNotEmpty()) {
            Log.d(TAG, "Processing ${earlyNotificationBuffer.size} buffered notifications")
            earlyNotificationBuffer.forEach { message ->
                processNotificationMessage(message)
            }
            earlyNotificationBuffer.clear()
        }
    }
    
    fun setOnDeviceUpdateListener(callback: () -> Unit) {
        onDeviceUpdateCallback = callback
    }
    
    fun setOnNotificationUpdateListener(callback: () -> Unit) {
        onNotificationUpdateCallback = callback
    }
    
    private val listener = object : WebSocketListener() {
        override fun onOpen(webSocket: WebSocket, response: Response) {
            Log.d(TAG, "WebSocket connection opened")
        }
          override fun onMessage(webSocket: WebSocket, text: String) {
            Log.d(TAG, "Received message: $text")
            try {
                // First, let's check if this is a JSON message
                val jsonObject = gson.fromJson(text, JsonObject::class.java)
                
                // Check if it has the expected structure
                if (jsonObject.has("method")) {
                    val method = jsonObject.get("method").asString
                    Log.d(TAG, "Processing method: $method")
                    
                    if (jsonObject.has("params")) {
                        val params = jsonObject.getAsJsonObject("params")
                        
                        when (method) {
                            "newDeviceConnected" -> {
                                handleNewDeviceConnected(params)
                                notifyDeviceUpdate()
                            }
                            "deviceUpdated" -> {
                                handleDeviceUpdated(params)
                                notifyDeviceUpdate()
                            }
                            "notification" -> {
                                Log.d(TAG, "Notification message received, UI ready: $isUIReady")
                                if (isUIReady) {
                                    handleNotification(params)
                                    notifyNotificationUpdate()
                                } else {
                                    // Buffer the message for later processing
                                    Log.d(TAG, "UI not ready, buffering notification message")
                                    earlyNotificationBuffer.add(text)
                                }
                            }
                            else -> Log.w(TAG, "Unknown method: $method")
                        }
                    } else {
                        Log.w(TAG, "Message with method '$method' has no params")
                    }
                } else {
                    // Handle messages that might be simple strings or different formats
                    Log.d(TAG, "Received non-method message, checking if it's a welcome message")
                    
                    // Check if it's a simple welcome message
                    if (text.contains("welcome", ignoreCase = true) || 
                        text.contains("connected", ignoreCase = true)) {
                        Log.d(TAG, "Detected welcome message: $text")
//                        createWelcomeNotification(text)
                    } else {
                        Log.w(TAG, "Unknown message format: $text")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error processing message: ${e.message}")
                Log.e(TAG, "Raw message was: $text")
                
                // Try to handle as simple text message
                if (text.contains("welcome", ignoreCase = true) || 
                    text.contains("connected", ignoreCase = true)) {
                    Log.d(TAG, "Treating as simple welcome message")
                    createWelcomeNotification(text)
                }
            }
        }
        
        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            Log.e(TAG, "WebSocket connection failed: ${t.message}")
            // Attempt to reconnect after a delay
            reconnect()
        }
        
        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            Log.d(TAG, "WebSocket connection closed: $reason")
        }
    }
    
    private fun notifyDeviceUpdate() {
        onDeviceUpdateCallback?.invoke()
    }
    
    private fun notifyNotificationUpdate() {
        onNotificationUpdateCallback?.invoke()
    }
    
    fun connect() {
        if (webSocket == null) {
            val request = Request.Builder()
                .url(WS_URL)
                .build()
            
            webSocket = client.newWebSocket(request, listener)
        }
    }
    
    fun disconnect() {
        webSocket?.close(1000, "Normal closure")
        webSocket = null
    }
    
    private fun reconnect() {
        disconnect()
        // Wait for 5 seconds before attempting to reconnect
        Thread.sleep(5000)
        connect()
    }
    
    fun sendMessage(message: JsonObject) {
        webSocket?.let { ws ->
            val messageString = message.toString()
            ws.send(messageString)
            Log.d(TAG, "Sent message: $messageString")
        } ?: run {
            Log.e(TAG, "Cannot send message: WebSocket is not connected")
            connect() // Attempt to reconnect
        }
    }
    
    // Test method to simulate receiving a notification message
    fun simulateNotificationMessage(notificationMessage: String) {
        Log.d(TAG, "Simulating notification message: $notificationMessage")
        try {
            val jsonObject = gson.fromJson(notificationMessage, JsonObject::class.java)
            val method = jsonObject.get("method").asString
            val params = jsonObject.getAsJsonObject("params")
            
            if (method == "notification") {
                handleNotification(params)
                notifyNotificationUpdate()
                Log.d(TAG, "Successfully processed simulated notification")
            } else {
                Log.w(TAG, "Simulated message is not a notification: $method")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error processing simulated notification: ${e.message}")
        }
    }
    
    private fun handleNewDeviceConnected(params: JsonObject) {
        try {
            val deviceParams = params.getAsJsonObject("device")
            val device = gson.fromJson(deviceParams, MCU::class.java)
            val office = RoomManager.getRoomByID(device.office_id)

            office?.let {
                it.addMCU(device)
                Log.d(TAG, "Added new device ${device.name} to office ${it.name}")
            } ?: Log.e(TAG, "Office with ID ${device.office_id} not found")
        } catch (e: Exception) {
            Log.e(TAG, "Error handling new device: ${e.message}")
        }
    }

    private fun handleDeviceUpdated(params: JsonObject) {
        try {
            val deviceParams = params.getAsJsonObject("device")
            val device = gson.fromJson(deviceParams, MCU::class.java)
            val office = RoomManager.getRoomByID(device.office_id)

            office?.let {
                val existingMCU = it.getMCUs().find { mcu -> mcu.id == device.id }
                if (existingMCU != null) {
                    // Update existing MCU
                    it.updateMCU(existingMCU, device)
                    Log.d(TAG, "Updated device ${device.name} in office ${it.name}")
                } else {
                    // Add as new MCU if not found
                    it.addMCU(device)
                    Log.d(TAG, "Added device ${device.name} to office ${it.name}")
                }
            } ?: Log.e(TAG, "Office with ID ${device.office_id} not found")        } catch (e: Exception) {
            Log.e(TAG, "Error handling device update: ${e.message}")
        }
    }
    
    private fun processNotificationMessage(text: String) {
        try {
            val jsonObject = gson.fromJson(text, JsonObject::class.java)
            val params = jsonObject.getAsJsonObject("params")
            handleNotification(params)
            notifyNotificationUpdate()
        } catch (e: Exception) {
            Log.e(TAG, "Error processing buffered notification: ${e.message}")
        }
    }

    private fun handleNotification(params: JsonObject) {
        try {
            // Set appropriate icon based on notification type
            val type = params.get("type").asString
            val iconRes = when (type.lowercase()) {
                "alert", "warning" -> R.drawable.ic_warning
                "device" -> R.drawable.ic_device
                "system" -> R.drawable.ic_settings
                "reminder" -> R.drawable.ic_reminder
                "info" -> R.drawable.ic_info
                else -> R.drawable.ic_notifications
            }
            
            // Format timestamp
            val ts = params.get("ts").asString
            val formattedTime = try {
                val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS", Locale.getDefault())
                inputFormat.timeZone = TimeZone.getTimeZone("UTC")
                val date = inputFormat.parse(ts)
                val outputFormat = SimpleDateFormat("HH:mm dd-MM-yyyy", Locale.getDefault())
                outputFormat.format(date ?: Date())
            } catch (e: Exception) {
                Log.e(TAG, "Error parsing timestamp: $ts", e)
                ts // Fallback to original timestamp
            }

            val notification = Notification(
                id = params.get("id").asInt,
                message = params.get("message").asString,
                read_status = params.get("read_status").asBoolean,
                type = type,
                title = params.get("title").asString,
                device_id = if (params.has("device_id") && !params.get("device_id").isJsonNull) 
                    params.get("device_id").asInt else 0,
                ts = formattedTime,
                iconRes = iconRes
            )
            Log.d(TAG, "Before adding new notification: ${notification.title} (ID: ${notification.id})")
            Log.d(TAG, "Total notifications in manager: ${NotificationManager.getNotificationCount()}")
              NotificationManager.addNotification(notification)
            Log.d(TAG, "Added new notification: ${notification.title} (ID: ${notification.id})")
            Log.d(TAG, "Total notifications in manager: ${NotificationManager.getNotificationCount()}")
            Log.d(TAG, "Unread notifications: ${NotificationManager.getUnreadCount()}")
        } catch (e: Exception) {
            Log.e(TAG, "Error handling notification: ${e.message}")
        }
    }
    
    private fun createWelcomeNotification(message: String) {
        try {
            val currentTime = SimpleDateFormat("HH:mm dd-MM-yyyy", Locale.getDefault()).format(Date())
            
            val welcomeNotification = Notification(
                id = System.currentTimeMillis().toInt(), // Generate unique ID
                message = message,
                read_status = false,
                type = "welcome",
                title = "Welcome",
                device_id = 0,
                ts = currentTime,
                iconRes = R.drawable.ic_info
            )
            
            if (isUIReady) {
                NotificationManager.addNotification(welcomeNotification)
                notifyNotificationUpdate()
                Log.d(TAG, "Added welcome notification: ${welcomeNotification.message}")
            } else {
                // If UI is not ready, we need to add it to NotificationManager anyway
                // since the buffering system only handles JSON messages
                NotificationManager.addNotification(welcomeNotification)
                Log.d(TAG, "Added welcome notification to manager (UI not ready): ${welcomeNotification.message}")
            }
            
            Log.d(TAG, "Total notifications after welcome: ${NotificationManager.getNotificationCount()}")
        } catch (e: Exception) {
            Log.e(TAG, "Error creating welcome notification: ${e.message}")
        }
    }
}