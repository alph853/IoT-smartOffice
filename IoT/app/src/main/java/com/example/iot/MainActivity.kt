package com.example.iot

import android.os.Bundle
import android.util.TypedValue
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.ViewTreeObserver
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.RelativeLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView

class MainActivity : AppCompatActivity() {
    private lateinit var yoloUno1Container: RelativeLayout
    private lateinit var yoloUno2Container: RelativeLayout
    private lateinit var statusYoloUno1: ImageView
    private lateinit var statusYoloUno2: ImageView
    private lateinit var sensorCardsContainer: LinearLayout
    private lateinit var addSensorButton: ImageButton
    private lateinit var initialSensorRow: LinearLayout
    private lateinit var removeDht20Button: ImageButton
    private lateinit var removeLightButton: ImageButton
    private var cardWidth = 0
    private var cardCount = 2 // Initial count (DHT20 and Light sensor)
    private val cardRows = mutableListOf<LinearLayout>()
    private val cardsInRow = mutableListOf<MutableList<CardView>>()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize MCU selection views
        setupMcuSelection()
        
        // Initialize sensor card adding functionality
        setupSensorCardAdding()
        
        // Set equal dimensions for sensor cards
        setupSquareSensorCards()
    }
    
    private fun setupMcuSelection() {
        // Find view references
        yoloUno1Container = findViewById(R.id.yolo_uno_1_container)
        yoloUno2Container = findViewById(R.id.yolo_uno_2_container)
        statusYoloUno1 = findViewById(R.id.status_yolo_uno_1)
        statusYoloUno2 = findViewById(R.id.status_yolo_uno_2)
        
        // Set initial state
        statusYoloUno1.visibility = View.VISIBLE
        statusYoloUno2.visibility = View.INVISIBLE
        
        // Set click listeners
        yoloUno1Container.setOnClickListener {
            // Select Yolo Uno 1
            statusYoloUno1.visibility = View.VISIBLE
            statusYoloUno2.visibility = View.INVISIBLE
        }
        
        yoloUno2Container.setOnClickListener {
            // Select Yolo Uno 2
            statusYoloUno1.visibility = View.INVISIBLE
            statusYoloUno2.visibility = View.VISIBLE
        }
    }
    
    private fun setupSensorCardAdding() {
        // Find view references
        sensorCardsContainer = findViewById(R.id.sensor_cards_container)
        addSensorButton = findViewById(R.id.add_sensor_button)
        initialSensorRow = findViewById(R.id.initial_sensor_row)
        removeDht20Button = findViewById(R.id.remove_dht20_button)
        removeLightButton = findViewById(R.id.remove_light_button)
        
        // Keep track of initial row and cards
        cardRows.add(initialSensorRow)
        cardsInRow.add(mutableListOf(
            findViewById(R.id.dht20_card),
            findViewById(R.id.light_card)
        ))
        
        // Set click listener for add button
        addSensorButton.setOnClickListener {
            addNewSensorCard()
        }
        
        // Set click listeners for remove buttons
        removeDht20Button.setOnClickListener {
            removeCard(0, 0) // Row 0, Card 0 (DHT20)
        }
        
        removeLightButton.setOnClickListener {
            removeCard(0, 1) // Row 0, Card 1 (Light)
        }
    }
    
    private fun addNewSensorCard() {
        // Find the last row or create a new one if needed
        var targetRow: LinearLayout
        var rowIndex: Int
        var cardIndex: Int
        
        // Get the last row
        if (cardRows.isNotEmpty()) {
            rowIndex = cardRows.size - 1
            targetRow = cardRows[rowIndex]
            val cards = cardsInRow[rowIndex]
            
            // If the last row already has 2 cards, create a new row
            if (cards.size >= 2) {
                val newRow = LinearLayout(this).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    ).apply {
                        bottomMargin = (cardWidth / 190) * 20
                    }
                    orientation = LinearLayout.HORIZONTAL
                    weightSum = 2f
                }
                
                sensorCardsContainer.addView(newRow)
                rowIndex = cardRows.size
                cardRows.add(newRow)
                cardsInRow.add(mutableListOf())
                targetRow = newRow
                cardIndex = 0
            } else {
                cardIndex = cards.size
            }
        } else {
            // Create first row
            val newRow = LinearLayout(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    bottomMargin = (cardWidth / 190) * 20
                }
                orientation = LinearLayout.HORIZONTAL
                weightSum = 2f
            }
            
            sensorCardsContainer.addView(newRow)
            rowIndex = 0
            cardRows.add(newRow)
            cardsInRow.add(mutableListOf())
            targetRow = newRow
            cardIndex = 0
        }
        
        // Create a new DHT20 card
        val newCard = createSensorCard(View.generateViewId(), true)
        val paddingSize = (cardWidth / 190) * 20
        
        // Set the layout parameters based on position
        if (cardIndex == 0) {
            // First card in the row gets end margin
            newCard.layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f).apply {
                marginEnd = paddingSize
            }
        } else {
            // Second card in the row has no margin
            newCard.layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }
        
        // Add the card to the target row
        targetRow.addView(newCard)
        
        // Track the new card
        cardsInRow[rowIndex].add(newCard)
        
        // Setup dimensions for the new card
        setupCardDimensions(newCard, newCard.id, rowIndex, cardIndex)
        
        // Increment card count
        cardCount++
    }
    
    private fun createSensorCard(cardId: Int, isDht20: Boolean = true): CardView {
        // Create the card view
        val cardView = CardView(this).apply {
            id = cardId
            layoutParams = LinearLayout.LayoutParams(
                0,
                ViewGroup.LayoutParams.WRAP_CONTENT,
                1f
            )
            radius = dipToPx(20f)
            setCardBackgroundColor(0xFF1C1C1E.toInt())
        }
        
        // Create FrameLayout to hold content and remove button
        val frameLayout = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }
        
        // Create the container for card content
        val containerId = View.generateViewId()
        val container = LinearLayout(this).apply {
            id = containerId
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
            setPadding(1, 1, 1, 1)
        }
        
        // Create the image view
        val imageId = View.generateViewId()
        val imageView = ImageView(this).apply {
            id = imageId
            layoutParams = LinearLayout.LayoutParams(
                1,
                1
            ).apply {
                bottomMargin = 1
            }
            setImageResource(if(isDht20) R.drawable.ic_temperature else R.drawable.ic_light)
        }
        
        // Create the title text view
        val titleId = View.generateViewId()
        val titleTextView = TextView(this).apply {
            id = titleId
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = 1
            }
            text = getString(if(isDht20) R.string.dht20 else R.string.light_sensor)
            setTextColor(0xFFFFFFFF.toInt())
            textSize = 20f
            gravity = android.view.Gravity.CENTER
            setTypeface(null, android.graphics.Typeface.BOLD)
        }
        
        // Create the description text view
        val descId = View.generateViewId()
        val descTextView = TextView(this).apply {
            id = descId
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            text = getString(R.string.sensor_description)
            setTextColor(0xFF919193.toInt())
            textSize = 14f
            gravity = android.view.Gravity.CENTER
        }
        
        // Create remove button
        val removeButtonId = View.generateViewId()
        val removeButton = ImageButton(this).apply {
            id = removeButtonId
            layoutParams = FrameLayout.LayoutParams(
                dipToPx(24f).toInt(),
                dipToPx(24f).toInt()
            ).apply {
                gravity = android.view.Gravity.TOP or android.view.Gravity.END
                setMargins(8, 8, 8, 8)
            }
            setImageResource(R.drawable.ic_remove)
            setBackgroundResource(android.R.color.transparent)
            contentDescription = "Remove sensor"
        }
        
        // Add views to container
        container.addView(imageView)
        container.addView(titleTextView)
        container.addView(descTextView)
        
        // Add container and remove button to FrameLayout
        frameLayout.addView(container)
        frameLayout.addView(removeButton)
        
        // Add FrameLayout to card
        cardView.addView(frameLayout)
        
        return cardView
    }
    
    private fun setupCardDimensions(cardView: CardView, cardId: Int, rowIndex: Int, cardIndex: Int) {
        // Wait for layout to get the card width
        cardView.viewTreeObserver.addOnGlobalLayoutListener(object : ViewTreeObserver.OnGlobalLayoutListener {
            override fun onGlobalLayout() {
                cardView.viewTreeObserver.removeOnGlobalLayoutListener(this)
                
                // Set card height equal to width
                val layoutParams = cardView.layoutParams
                layoutParams.height = cardWidth
                cardView.layoutParams = layoutParams
                
                // Find the views by their IDs
                val frameLayout = cardView.getChildAt(0) as FrameLayout
                val container = frameLayout.getChildAt(0) as LinearLayout
                val removeButton = frameLayout.getChildAt(1) as ImageButton
                val imageView = container.getChildAt(0) as ImageView
                val titleTextView = container.getChildAt(1) as TextView
                val descTextView = container.getChildAt(2) as TextView
                
                // Calculate sizes
                val paddingSize = (cardWidth / 190) * 20
                val imageSize = (cardWidth / 190) * 64
                val titleTextSize = (cardWidth / 190f) * 20f
                val descTextSize = (cardWidth / 190f) * 12f
                
                // Set padding
                container.setPadding(paddingSize, paddingSize, paddingSize, paddingSize)
                
                // Set image size
                val imageParams = imageView.layoutParams
                imageParams.width = imageSize
                imageParams.height = imageSize
                imageView.layoutParams = imageParams
                
                // Set margins between elements
                val marginParams1 = imageView.layoutParams as ViewGroup.MarginLayoutParams
                marginParams1.bottomMargin = paddingSize
                imageView.layoutParams = marginParams1
                
                val marginParams3 = titleTextView.layoutParams as ViewGroup.MarginLayoutParams
                marginParams3.bottomMargin = paddingSize / 20 * 12
                titleTextView.layoutParams = marginParams3
                
                // Set text sizes
                titleTextView.setTextSize(TypedValue.COMPLEX_UNIT_PX, titleTextSize)
                descTextView.setTextSize(TypedValue.COMPLEX_UNIT_PX, descTextSize)
                
                // Set click listener for remove button
                removeButton.setOnClickListener {
                    removeCard(rowIndex, cardIndex)
                }
            }
        })
    }
    
    private fun removeCard(rowIndex: Int, cardIndex: Int) {
        // Prevent removing all cards
        if (cardCount <= 0) {
            return
        }

        try {
            // Get the row and card to remove
            val row = cardRows[rowIndex]
            val cards = cardsInRow[rowIndex]
            val cardToRemove = cards[cardIndex]
            
            // Remove the card from the view and tracking data
            row.removeView(cardToRemove)
            cards.removeAt(cardIndex)
            cardCount--
            
            // Rearrange all cards after removal
            rearrangeCards()
        } catch (e: Exception) {
            // Handle any exceptions (index out of bounds, etc.)
            e.printStackTrace()
        }
    }
    
    private fun rearrangeCards() {
        // Create a list to hold all remaining cards in order
        val allCards = mutableListOf<CardView>()
        
        // Collect all cards from all rows
        for (cards in cardsInRow) {
            allCards.addAll(cards)
        }
        
        // Remember dimensions of the first card (if available) to ensure consistency
        val originalPaddingSize = (cardWidth / 190) * 20
        
        // Keep reference to the original first row
        val firstRow = cardRows[0]
        
        // Save the firstRow dimensions and properties before clearing
        val firstRowParams = firstRow.layoutParams as LinearLayout.LayoutParams
        val firstRowBottomMargin = firstRowParams.bottomMargin
        val firstRowOrientation = firstRow.orientation
        val firstRowWeightSum = firstRow.weightSum
        
        // Clear the first row but keep it in the layout
        firstRow.removeAllViews()
        
        // Clear all rows except the first one
        for (i in cardRows.size - 1 downTo 1) {
            sensorCardsContainer.removeView(cardRows[i])
        }
        
        // Clear all tracking data
        cardRows.clear()
        cardsInRow.clear()
        
        // Re-add the first row to tracking with original properties
        firstRow.orientation = firstRowOrientation
        firstRow.weightSum = firstRowWeightSum
        firstRowParams.bottomMargin = firstRowBottomMargin
        firstRow.layoutParams = firstRowParams
        
        cardRows.add(firstRow)
        cardsInRow.add(mutableListOf())
        
        // Re-add all cards, creating new rows as needed
        for (card in allCards) {
            // Get the current row
            var currentRow = cardRows.last()
            var currentRowCards = cardsInRow.last()
            
            // If current row is full (has 2 cards), create a new row
            if (currentRowCards.size >= 2) {
                val newRow = LinearLayout(this).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    ).apply {
                        bottomMargin = originalPaddingSize
                    }
                    orientation = LinearLayout.HORIZONTAL
                    weightSum = 2f
                }
                
                sensorCardsContainer.addView(newRow)
                cardRows.add(newRow)
                cardsInRow.add(mutableListOf())
                
                currentRow = newRow
                currentRowCards = cardsInRow.last()
            }
            
            // Remove card from its parent if it has one
            (card.parent as? ViewGroup)?.removeView(card)
            
            // Set card layout params based on position
            if (currentRowCards.size == 0) {
                // First card in row gets end margin
                card.layoutParams = LinearLayout.LayoutParams(0, cardWidth, 1f).apply {
                    marginEnd = originalPaddingSize
                }
            } else {
                // Second card in row has no margin
                card.layoutParams = LinearLayout.LayoutParams(0, cardWidth, 1f)
            }
            
            // Add card to row
            currentRow.addView(card)
            currentRowCards.add(card)
            
            // Update remove button listener
            val frameLayout = card.getChildAt(0) as FrameLayout
            val removeButton = frameLayout.getChildAt(1) as ImageButton
            val rowIndex = cardRows.indexOf(currentRow)
            val cardIndex = currentRowCards.size - 1
            removeButton.setOnClickListener {
                removeCard(rowIndex, cardIndex)
            }
            
            // Ensure card content is properly sized
            ensureCardContentSizes(card)
        }
    }
    
    private fun ensureCardContentSizes(card: CardView) {
        // Find the views within the card
        val frameLayout = card.getChildAt(0) as FrameLayout
        val container = frameLayout.getChildAt(0) as LinearLayout
        val imageView = container.getChildAt(0) as ImageView
        val titleTextView = container.getChildAt(1) as TextView
        val descTextView = container.getChildAt(2) as TextView
        
        // Calculate sizes
        val paddingSize = (cardWidth / 190) * 20
        val imageSize = (cardWidth / 190) * 64
        val titleTextSize = (cardWidth / 190f) * 20f
        val descTextSize = (cardWidth / 190f) * 12f
        
        // Set padding
        container.setPadding(paddingSize, paddingSize, paddingSize, paddingSize)
        
        // Set image size
        val imageParams = imageView.layoutParams
        imageParams.width = imageSize
        imageParams.height = imageSize
        imageView.layoutParams = imageParams
        
        // Set margins between elements
        val marginParams1 = imageView.layoutParams as ViewGroup.MarginLayoutParams
        marginParams1.bottomMargin = paddingSize
        imageView.layoutParams = marginParams1
        
        val marginParams3 = titleTextView.layoutParams as ViewGroup.MarginLayoutParams
        marginParams3.bottomMargin = paddingSize / 20 * 12
        titleTextView.layoutParams = marginParams3
        
        // Set text sizes
        titleTextView.setTextSize(TypedValue.COMPLEX_UNIT_PX, titleTextSize)
        descTextView.setTextSize(TypedValue.COMPLEX_UNIT_PX, descTextSize)
    }
    
    private fun dipToPx(dp: Float): Float {
        return TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            dp,
            resources.displayMetrics
        )
    }
    
    private fun setupSquareSensorCards() {
        val dht20Card = findViewById<CardView>(R.id.dht20_card)
        val lightCard = findViewById<CardView>(R.id.light_card)
        val dht20Container = findViewById<LinearLayout>(R.id.dht20_container)
        val lightContainer = findViewById<LinearLayout>(R.id.light_container)
        val dht20Image = findViewById<ImageView>(R.id.dht20_image)
        val lightImage = findViewById<ImageView>(R.id.light_image)
        val dht20Title = findViewById<TextView>(R.id.dht20_title)
        val lightTitle = findViewById<TextView>(R.id.light_title)
        val dht20Description = findViewById<TextView>(R.id.dht20_description)
        val lightDescription = findViewById<TextView>(R.id.light_description)
        
        // Use ViewTreeObserver to get dimensions after layout is complete
        val linearLayout = dht20Card.parent.parent as LinearLayout
        linearLayout.viewTreeObserver.addOnGlobalLayoutListener(object : ViewTreeObserver.OnGlobalLayoutListener {
            override fun onGlobalLayout() {
                // Remove the listener to prevent multiple calls
                linearLayout.viewTreeObserver.removeOnGlobalLayoutListener(this)
                
                // Get card width after layout is complete
                cardWidth = dht20Card.width
                
                // Calculate padding/margin size using formula: card width / 190 * 20
                val paddingSize = (cardWidth / 190) * 20
                
                // Set container padding
                dht20Container.setPadding(paddingSize, paddingSize, paddingSize, paddingSize)
                lightContainer.setPadding(paddingSize, paddingSize, paddingSize, paddingSize)
                
                // Set card heights equal to their widths
                val layoutParams1 = dht20Card.layoutParams
                layoutParams1.height = cardWidth
                dht20Card.layoutParams = layoutParams1
                
                val layoutParams2 = lightCard.layoutParams
                layoutParams2.height = cardWidth
                lightCard.layoutParams = layoutParams2
                
                // Calculate image size using formula: card width / 190 * 64
                val imageSize = (cardWidth / 190) * 64
                
                // Set image dimensions proportionally
                val imageParams1 = dht20Image.layoutParams
                imageParams1.width = imageSize
                imageParams1.height = imageSize
                dht20Image.layoutParams = imageParams1
                
                val imageParams2 = lightImage.layoutParams
                imageParams2.width = imageSize
                imageParams2.height = imageSize
                lightImage.layoutParams = imageParams2
                
                // Set margins between elements
                val marginParams1 = dht20Image.layoutParams as ViewGroup.MarginLayoutParams
                marginParams1.bottomMargin = paddingSize
                dht20Image.layoutParams = marginParams1
                
                val marginParams2 = lightImage.layoutParams as ViewGroup.MarginLayoutParams
                marginParams2.bottomMargin = paddingSize
                lightImage.layoutParams = marginParams2
                
                val marginParams3 = dht20Title.layoutParams as ViewGroup.MarginLayoutParams
                marginParams3.bottomMargin = paddingSize / 20 * 12
                dht20Title.layoutParams = marginParams3
                
                val marginParams4 = lightTitle.layoutParams as ViewGroup.MarginLayoutParams
                marginParams4.bottomMargin = paddingSize / 20 * 12
                lightTitle.layoutParams = marginParams4
                
                // Set text sizes using the same formula
                // Title text size (originally 20sp)
                val titleTextSize = (cardWidth / 190f) * 20f
                dht20Title.setTextSize(TypedValue.COMPLEX_UNIT_PX, titleTextSize)
                lightTitle.setTextSize(TypedValue.COMPLEX_UNIT_PX, titleTextSize)
                
                // Description text size (originally 14sp)
                val descTextSize = (cardWidth / 190f) * 12f
                dht20Description.setTextSize(TypedValue.COMPLEX_UNIT_PX, descTextSize)
                lightDescription.setTextSize(TypedValue.COMPLEX_UNIT_PX, descTextSize)
            }
        })
    }
}