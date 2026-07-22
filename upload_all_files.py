#!/usr/bin/env python3
import base64
import subprocess
import sys
import time

BASE = "/storage/emulated/0/AndroidCSProjects/aidevtoolbox/app/src/main/kotlin/com/erople/mybasic/aidevtoolbox"

def upload(content, remote_path):
    """Upload content to remote path using shizuku"""
    b64 = base64.b64encode(content.encode('utf-8')).decode()
    chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]
    
    # Create tmp dir
    subprocess.run(['shizuku', 'sh', '-c', 'mkdir -p /sdcard/tmp'], capture_output=True, timeout=10)
    
    # Remove old file
    subprocess.run(['shizuku', 'sh', '-c', f"rm -f '{remote_path}'"], capture_output=True, timeout=10)
    
    # Write chunks
    subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"], capture_output=True, timeout=30)
    for c in chunks[1:]:
        subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{c}' >> /sdcard/tmp/up.b64"], capture_output=True, timeout=15)
    
    # Decode and save
    result = subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{remote_path}' && rm /sdcard/tmp/up.b64"], capture_output=True, timeout=20)
    
    return result.returncode == 0

def verify(remote_path):
    """Verify file was uploaded correctly"""
    result = subprocess.run(['shizuku', 'sh', 'sh', '-c', f"wc -c < '{remote_path}'"], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        size = result.stdout.strip()
        # Get first 5 lines
        head = subprocess.run(['shizuku', 'sh', 'sh', '-c', f"head -5 '{remote_path}'"], capture_output=True, text=True, timeout=10)
        print(f"  ✅ {size} bytes | {head.stdout.strip()[:80]}")
        return int(size)
    else:
        print(f"  ❌ Verification failed")
        return 0

# All file contents
files = {}

# 1. core/BaseFragment.kt
files[f"{BASE}/core/BaseFragment.kt"] = '''package com.erople.mybasic.aidevtoolbox.core

import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import android.view.ViewGroup
import android.view.LayoutInflater
import androidx.fragment.app.Fragment
import com.erople.mybasic.aidevtoolbox.R

abstract class BaseFragment : Fragment() {
    private var progressBar: ProgressBar? = null
    private var errorContainer: View? = null
    private var errorText: TextView? = null
    private var retryButton: View? = null
    private var offlineContainer: View? = null
    private var emptyContainer: View? = null
    private var skeletonContainer: View? = null
    private var contentContainer: View? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        findViews(view)
        setupViews(view)
        observeData()
    }

    private fun findViews(view: View) {
        progressBar = view.findViewById(R.id.progress_bar)
        errorContainer = view.findViewById(R.id.error_container)
        errorText = view.findViewById(R.id.error_text)
        retryButton = view.findViewById(R.id.retry_button)
        offlineContainer = view.findViewById(R.id.offline_container)
        emptyContainer = view.findViewById(R.id.empty_container)
        skeletonContainer = view.findViewById(R.id.skeleton_container)
        contentContainer = view.findViewById(R.id.content_container)
    }

    open fun setupViews(view: View) {}
    abstract fun observeData()

    fun showLoading() {
        progressBar?.visibility = View.VISIBLE
        contentContainer?.visibility = View.GONE
        errorContainer?.visibility = View.GONE
        offlineContainer?.visibility = View.GONE
        emptyContainer?.visibility = View.GONE
        skeletonContainer?.visibility = View.GONE
    }

    fun showSkeleton() {
        skeletonContainer?.visibility = View.VISIBLE
        contentContainer?.visibility = View.GONE
        progressBar?.visibility = View.GONE
        errorContainer?.visibility = View.GONE
        offlineContainer?.visibility = View.GONE
        emptyContainer?.visibility = View.GONE
    }

    fun showContent() {
        contentContainer?.visibility = View.VISIBLE
        progressBar?.visibility = View.GONE
        errorContainer?.visibility = View.GONE
        offlineContainer?.visibility = View.GONE
        emptyContainer?.visibility = View.GONE
        skeletonContainer?.visibility = View.GONE
    }

    fun showError(message: String) {
        errorContainer?.visibility = View.VISIBLE
        errorText?.text = message
        contentContainer?.visibility = View.GONE
        progressBar?.visibility = View.GONE
        offlineContainer?.visibility = View.GONE
        emptyContainer?.visibility = View.GONE
        skeletonContainer?.visibility = View.GONE
    }

    fun setupRetry(onRetry: () -> Unit) {
        retryButton?.setOnClickListener { onRetry() }
    }

    fun showOffline() {
        offlineContainer?.visibility = View.VISIBLE
        contentContainer?.visibility = View.GONE
        progressBar?.visibility = View.GONE
        errorContainer?.visibility = View.GONE
        emptyContainer?.visibility = View.GONE
        skeletonContainer?.visibility = View.GONE
    }

    fun showEmpty() {
        emptyContainer?.visibility = View.VISIBLE
        contentContainer?.visibility = View.GONE
        progressBar?.visibility = View.GONE
        errorContainer?.visibility = View.GONE
        offlineContainer?.visibility = View.GONE
        skeletonContainer?.visibility = View.GONE
    }

    fun <T> handleState(state: ViewState<T>, onSuccess: (T) -> Unit) {
        when (state) {
            is ViewState.Loading -> showLoading()
            is ViewState.Skeleton -> showSkeleton()
            is ViewState.Empty -> showEmpty()
            is ViewState.Offline -> showOffline()
            is ViewState.Timeout -> showError(getString(R.string.error_timeout))
            is ViewState.Error -> showError(state.message)
            is ViewState.Success -> { showContent(); onSuccess(state.data) }
        }
    }

    fun isNetworkAvailable(): Boolean = NetworkMonitor.isConnected()
}
'''

# 2. core/Extensions.kt
files[f"{BASE}/core/Extensions.kt"] = '''package com.erople.mybasic.aidevtoolbox.core

import android.app.Activity
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.inputmethod.InputMethodManager
import android.widget.EditText
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit
import kotlin.math.ln
import kotlin.math.pow

fun Context.toast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

fun Fragment.toast(message: String) {
    context?.toast(message)
}

fun Context.copyToClipboard(text: String, label: String = "text") {
    val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
    val clip = ClipData.newPlainText(label, text)
    clipboard.setPrimaryClip(clip)
    toast("Copied to clipboard")
}

fun Context.dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
fun Context.sp(value: Int): Int = (value * resources.displayMetrics.scaledDensity).toInt()
fun View.dp(value: Int): Int = context.dp(value)
fun View.sp(value: Int): Int = context.sp(value)
fun Fragment.dp(value: Int): Int = requireContext().dp(value)

fun Context.color(resId: Int): Int = ContextCompat.getColor(this, resId)
fun Fragment.color(resId: Int): Int = requireContext().color(resId)

fun Context.showKeyboard(editText: EditText) {
    editText.requestFocus()
    val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
    imm.showSoftInput(editText, InputMethodManager.SHOW_IMPLICIT)
}

fun Context.hideKeyboard() {
    val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
    val currentFocus = (this as? Activity)?.currentFocus
    currentFocus?.let {
        imm.hideSoftInputFromWindow(it.windowToken, 0)
    }
}

fun Long.formatFileSize(): String {
    if (this <= 0) return "0 B"
    val units = arrayOf("B", "KB", "MB", "GB", "TB")
    val digitGroups = (ln(this.toDouble()) / ln(1024.0)).toInt().coerceAtMost(units.size - 1)
    return "%.1f %s".format(this / 1024.0.pow(digitGroups.toDouble()), units[digitGroups])
}

fun Long.formatDate(): String {
    val now = System.currentTimeMillis()
    val diff = now - this
    return when {
        diff < TimeUnit.MINUTES.toMillis(1) -> "Just now"
        diff < TimeUnit.HOURS.toMillis(1) -> "${diff / TimeUnit.MINUTES.toMillis(1)}m ago"
        diff < TimeUnit.DAYS.toMillis(1) -> "${diff / TimeUnit.HOURS.toMillis(1)}h ago"
        diff < TimeUnit.DAYS.toMillis(7) -> "${diff / TimeUnit.DAYS.toMillis(1)}d ago"
        else -> SimpleDateFormat("MMM dd, yyyy", Locale.getDefault()).format(Date(this))
    }
}

fun Long.formatFullDate(): String =
    SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault()).format(Date(this))

fun View.visible() { visibility = View.VISIBLE }
fun View.gone() { visibility = View.GONE }
fun View.invisible() { visibility = View.INVISIBLE }

fun postDelayed(delayMs: Long, action: () -> Unit) {
    Handler(Looper.getMainLooper()).postDelayed(action, delayMs)
}

fun String.getFileExtension(): String = substringAfterLast('.', "").lowercase()
fun String.isImageFile(): Boolean = getFileExtension() in setOf("jpg","jpeg","png","gif","webp","svg","bmp")
fun String.isCodeFile(): Boolean = getFileExtension() in setOf("kt","java","py","js","ts","html","css","json","xml","gradle","sh","sql")
'''

# 3. core/ErrorHandler.kt
files[f"{BASE}/core/ErrorHandler.kt"] = '''package com.erople.mybasic.aidevtoolbox.core

import android.util.Log
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object ErrorHandler {
    private const val TAG = "DevToolBox"

    fun handleCrash(thread: Thread, throwable: Throwable) {
        Log.e(TAG, "Uncaught exception: ${thread.name}", throwable)
    }

    fun handleError(throwable: Throwable, context: String = ""): String {
        val message = throwable.localizedMessage ?: throwable.message ?: "Unknown error"
        Log.e(TAG, "Error in $context: $message", throwable)
        return message
    }

    fun handleApiError(code: Int, message: String): String {
        val errorMsg = when (code) {
            400 -> "Bad request"
            401 -> "Unauthorized"
            403 -> "Forbidden"
            404 -> "Not found"
            429 -> "Too many requests"
            500 -> "Server error"
            else -> "Error $code: $message"
        }
        Log.e(TAG, "API Error $code: $errorMsg")
        return errorMsg
    }

    fun log(message: String, level: LogLevel = LogLevel.INFO) {
        when (level) {
            LogLevel.DEBUG -> Log.d(TAG, message)
            LogLevel.INFO -> Log.i(TAG, message)
            LogLevel.WARNING -> Log.w(TAG, message)
            LogLevel.ERROR -> Log.e(TAG, message)
        }
    }

    fun getErrorLogs(): String = "No error logs"
    fun clearErrorLogs() {}
}

enum class LogLevel { DEBUG, INFO, WARNING, ERROR }
'''

# 4. core/CacheManager.kt
files[f"{BASE}/core/CacheManager.kt"] = '''package com.erople.mybasic.aidevtoolbox.core

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import java.io.File
import java.io.FileOutputStream

object CacheManager {
    private lateinit var context: Context

    private val memoryCache = object : LruCache<String, Any>(Constants.CACHE_MAX_ENTRIES) {
        override fun sizeOf(key: String, value: Any): Int = 1
    }

    private val diskCacheDir: File by lazy {
        File(context.cacheDir, "devtoolbox_cache").apply { mkdirs() }
    }

    fun init(context: Context) {
        this.context = context.applicationContext
    }

    fun <T : Any> putMemory(key: String, value: T) = memoryCache.put(key, value)
    fun <T : Any> getMemory(key: String): T? = memoryCache.get(key) as? T
    fun removeMemory(key: String) = memoryCache.remove(key)
    fun clearMemory() = memoryCache.evictAll()

    fun putDisk(key: String, data: ByteArray) {
        val file = File(diskCacheDir, key.hashCode().toString())
        try {
            FileOutputStream(file).use { it.write(data) }
        } catch (_: Exception) {}
    }

    fun getDisk(key: String): ByteArray? {
        val file = File(diskCacheDir, key.hashCode().toString())
        return if (file.exists() && file.isFile) file.readBytes() else null
    }

    fun removeDisk(key: String) {
        File(diskCacheDir, key.hashCode().toString()).delete()
    }

    fun clearDisk() {
        diskCacheDir.listFiles()?.forEach { it.delete() }
    }

    fun clearAll() {
        clearMemory()
        clearDisk()
    }

    fun putImage(key: String, bitmap: Bitmap) {
        putMemory("img_$key", bitmap)
        try {
            val file = File(diskCacheDir, "img_${key.hashCode()}")
            FileOutputStream(file).use { bitmap.compress(Bitmap.CompressFormat.PNG, 100, it) }
        } catch (_: Exception) {}
    }

    fun getImage(key: String): Bitmap? {
        val memKey = "img_$key"
        getMemory<Bitmap>(memKey)?.let { return it }
        val file = File(diskCacheDir, "img_${key.hashCode()}")
        return if (file.exists()) {
            BitmapFactory.decodeFile(file.absolutePath)?.also { putMemory(memKey, it) }
        } else null
    }

    fun getCacheSize(): Long = diskCacheDir.listFiles()?.sumOf { it.length() } ?: 0L

    fun formatCacheSize(): String = getCacheSize().formatFileSize()
}
'''

# 5. core/NetworkMonitor.kt
files[f"{BASE}/core/NetworkMonitor.kt"] = '''package com.erople.mybasic.aidevtoolbox.core

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData

object NetworkMonitor : ConnectivityManager.NetworkCallback() {
    private lateinit var connectivityManager: ConnectivityManager
    private val _networkState = MutableLiveData<NetworkState>(NetworkState.Disconnected)
    val networkState: LiveData<NetworkState> = _networkState

    fun init(context: Context) {
        connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()
        connectivityManager.registerNetworkCallback(request, this)
        val activeNetwork = connectivityManager.activeNetwork
        val caps = activeNetwork?.let { connectivityManager.getNetworkCapabilities(it) }
        val connected = caps?.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) == true
        _networkState.postValue(if (connected) NetworkState.Connected else NetworkState.Disconnected)
    }

    fun isConnected(): Boolean = _networkState.value == NetworkState.Connected

    override fun onAvailable(network: Network) {
        _networkState.postValue(NetworkState.Connected)
    }

    override fun onLost(network: Network) {
        _networkState.postValue(NetworkState.Disconnected)
    }

    override fun onCapabilitiesChanged(network: Network, caps: NetworkCapabilities) {
        val metered = !caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED)
        _networkState.postValue(if (metered) NetworkState.Metered else NetworkState.Connected)
    }
}
'''

# 6. core/RetryPolicy.kt
files[f"{BASE}/core/RetryPolicy.kt"] = '''package com.erople.mybasic.aidevtoolbox.core

import kotlinx.coroutines.delay

object RetryPolicy {

    suspend fun <T> execute(
        maxAttempts: Int = Constants.RETRY_MAX_ATTEMPTS,
        initialDelayMs: Long = Constants.RETRY_DELAY_MS,
        backoffMultiplier: Double = Constants.RETRY_BACKOFF_MULTIPLIER,
        onError: ((Throwable, Int) -> Unit)? = null,
        block: suspend () -> T
    ): T {
        var currentDelay = initialDelayMs
        var lastException: Throwable? = null

        repeat(maxAttempts) { attempt ->
            try {
                return block()
            } catch (e: Exception) {
                lastException = e
                onError?.invoke(e, attempt + 1)
                ErrorHandler.log("Retry attempt ${attempt + 1}/$maxAttempts: ${e.message}", LogLevel.WARNING)
                if (attempt < maxAttempts - 1) {
                    delay(currentDelay)
                    currentDelay = (currentDelay * backoffMultiplier).toLong()
                }
            }
        }
        throw lastException ?: Exception("Retry failed after $maxAttempts attempts")
    }
}
'''

# 7. core/AnimUtils.kt
files[f"{BASE}/core/AnimUtils.kt"] = '''package com.erople.mybasic.aidevtoolbox.core

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.OvershootInterpolator
import android.view.animation.DecelerateInterpolator
import android.view.animation.LinearInterpolator

object AnimUtils {

    fun fadeIn(view: View, duration: Long = Constants.ANIM_DURATION_MEDIUM) {
        view.alpha = 0f
        view.visible()
        ObjectAnimator.ofFloat(view, "alpha", 0f, 1f).apply {
            this.duration = duration
            interpolator = DecelerateInterpolator()
            start()
        }
    }

    fun fadeOut(view: View, duration: Long = Constants.ANIM_DURATION_MEDIUM, onEnd: (() -> Unit)? = null) {
        ObjectAnimator.ofFloat(view, "alpha", 1f, 0f).apply {
            this.duration = duration
            interpolator = AccelerateDecelerateInterpolator()
            addListener(object : android.animation.AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: android.animation.Animator) {
                    view.gone()
                    onEnd?.invoke()
                }
            })
            start()
        }
    }

    fun slideUp(view: View, duration: Long = Constants.ANIM_DURATION_MEDIUM) {
        view.translationY = view.height.toFloat()
        view.visible()
        ObjectAnimator.ofFloat(view, "translationY", view.height.toFloat(), 0f).apply {
            this.duration = duration
            interpolator = DecelerateInterpolator()
            start()
        }
    }

    fun slideDown(view: View, duration: Long = Constants.ANIM_DURATION_MEDIUM) {
        ObjectAnimator.ofFloat(view, "translationY", 0f, view.height.toFloat()).apply {
            this.duration = duration
            interpolator = AccelerateDecelerateInterpolator()
            addListener(object : android.animation.AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: android.animation.Animator) { view.gone() }
            })
            start()
        }
    }

    fun bounceIn(view: View, duration: Long = Constants.ANIM_DURATION_LONG) {
        view.scaleX = 0f; view.scaleY = 0f
        view.visible()
        AnimatorSet().apply {
            playTogether(
                ObjectAnimator.ofFloat(view, "scaleX", 0f, 1f),
                ObjectAnimator.ofFloat(view, "scaleY", 0f, 1f)
            )
            this.duration = duration
            interpolator = OvershootInterpolator(1.5f)
            start()
        }
    }

    fun pulse(view: View, duration: Long = 1000L): ValueAnimator {
        return ValueAnimator.ofFloat(1f, 0.5f, 1f).apply {
            this.duration = duration
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener { view.alpha = it.animatedValue as Float }
            start()
        }
    }

    fun shake(view: View) {
        ObjectAnimator.ofFloat(view, "translationX", 0f, 25f, -25f, 20f, -20f, 15f, -15f, 0f).apply {
            duration = Constants.ANIM_DURATION_LONG
            start()
        }
    }

    fun rotate(view: View, from: Float = 0f, to: Float = 360f, duration: Long = 1000L): ObjectAnimator {
        return ObjectAnimator.ofFloat(view, "rotation", from, to).apply {
            this.duration = duration
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
        }
    }

    fun crossFade(hideView: View, showView: View, duration: Long = Constants.ANIM_DURATION_MEDIUM) {
        showView.visible()
        AnimatorSet().apply {
            playTogether(
                ObjectAnimator.ofFloat(hideView, "alpha", 1f, 0f),
                ObjectAnimator.ofFloat(showView, "alpha", 0f, 1f)
            )
            this.duration = duration
            addListener(object : android.animation.AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: android.animation.Animator) { hideView.gone() }
            })
            start()
        }
    }
}
'''

# 8. data/model/ChatMessage.kt
files[f"{BASE}/data/model/ChatMessage.kt"] = '''package com.erople.mybasic.aidevtoolbox.data.model

data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val content: String,
    val role: MessageRole,
    val timestamp: Long = System.currentTimeMillis(),
    val isStreaming: Boolean = false,
    val tokenCount: Int = 0,
    val model: String = "",
    val images: List<String> = emptyList(),
    val files: List<String> = emptyList(),
    val codeBlocks: List<CodeBlock> = emptyList()
)

enum class MessageRole { USER, ASSISTANT, SYSTEM }

data class CodeBlock(
    val language: String,
    val code: String,
    val startLine: Int = 1
)

data class ChatSession(
    val id: String = java.util.UUID.randomUUID().toString(),
    val title: String,
    val messages: MutableList<ChatMessage> = mutableListOf(),
    val createdAt: Long = System.currentTimeMillis(),
    val lastMessageAt: Long = System.currentTimeMillis(),
    val model: String = "default"
)
'''

# 9. data/model/ToolItem.kt
files[f"{BASE}/data/model/ToolItem.kt"] = '''package com.erople.mybasic.aidevtoolbox.data.model

data class ToolItem(
    val id: String,
    val name: String,
    val description: String,
    val iconRes: Int = 0,
    val category: ToolCategory,
    val isPremium: Boolean = false
)

enum class ToolCategory { ENCODER, GENERATOR, CONVERTER, VIEWER, EDITOR, TESTING }
'''

# 10. data/repository/FileRepository.kt
files[f"{BASE}/data/repository/FileRepository.kt"] = '''package com.erople.mybasic.aidevtoolbox.data.repository

import com.erople.mybasic.aidevtoolbox.core.Constants
import com.erople.mybasic.aidevtoolbox.data.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.util.UUID

class FileRepository {

    suspend fun getFiles(
        path: String,
        sortField: SortField = SortField.NAME,
        sortOrder: SortOrder = SortOrder.ASCENDING,
        filter: FilterType = FilterType.ALL,
        showHidden: Boolean = false
    ): List<FileItem> = withContext(Dispatchers.IO) {
        try {
            val dir = File(path)
            if (!dir.exists() || !dir.isDirectory) return@withContext emptyList()

            val files = dir.listFiles()
                ?.filter { showHidden || !it.name.startsWith(".") }
                ?.map { file ->
                    FileItem(
                        name = file.name,
                        path = file.absolutePath,
                        isDirectory = file.isDirectory,
                        size = if (file.isFile) file.length() else 0L,
                        lastModified = file.lastModified(),
                        extension = if (file.isFile) file.extension.lowercase() else "",
                        isHidden = file.name.startsWith(".")
                    )
                } ?: emptyList()

            val filtered = filterFiles(files, filter)
            sortFiles(filtered, sortField, sortOrder)
        } catch (_: Exception) {
            emptyList()
        }
    }

    private fun filterFiles(files: List<FileItem>, filter: FilterType): List<FileItem> {
        if (filter == FilterType.ALL) return files
        return files.filter { it.isDirectory || when (filter) {
            FilterType.IMAGES -> it.type == FileType.IMAGE
            FilterType.VIDEOS -> it.type == FileType.VIDEO
            FilterType.AUDIO -> it.type == FileType.AUDIO
            FilterType.DOCUMENTS -> it.type == FileType.DOCUMENT
            FilterType.CODE -> it.type == FileType.CODE
            FilterType.ARCHIVES -> it.type == FileType.ARCHIVE
            else -> true
        }}
    }

    private fun sortFiles(files: List<FileItem>, field: SortField, order: SortOrder): List<FileItem> {
        val sorted = when (field) {
            SortField.NAME -> files.sortedBy { it.name.lowercase() }
            SortField.SIZE -> files.sortedBy { if (it.isDirectory) Long.MAX_VALUE else it.size }
            SortField.DATE -> files.sortedBy { it.lastModified }
            SortField.TYPE -> files.sortedBy { it.extension }
        }
        return if (order == SortOrder.DESCENDING) sorted.reversed() else sorted
    }

    suspend fun createFolder(path: String, name: String): Boolean = withContext(Dispatchers.IO) {
        try { File(path, name).mkdirs() } catch (_: Exception) { false }
    }

    suspend fun renameFile(path: String, newName: String): Boolean = withContext(Dispatchers.IO) {
        try { File(path).renameTo(File(File(path).parent, newName)) } catch (_: Exception) { false }
    }

    suspend fun deleteFile(path: String): Boolean = withContext(Dispatchers.IO) {
        try { File(path).deleteRecursively() } catch (_: Exception) { false }
    }

    suspend fun copyFile(source: String, destDir: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val sourceFile = File(source)
            val destFile = File(destDir, sourceFile.name)
            sourceFile.copyTo(destFile, overwrite = true)
            true
        } catch (_: Exception) { false }
    }

    suspend fun moveFile(source: String, destDir: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val sourceFile = File(source)
            val destFile = File(destDir, sourceFile.name)
            sourceFile.renameTo(destFile)
        } catch (_: Exception) { false }
    }

    suspend fun searchFiles(path: String, query: String): List<FileItem> = withContext(Dispatchers.IO) {
        try {
            val dir = File(path)
            val results = mutableListOf<FileItem>()
            dir.walkTopDown()
                .maxDepth(5)
                .filter { it.name.contains(query, ignoreCase = true) }
                .take(100)
                .forEach { file ->
                    results.add(FileItem(
                        name = file.name,
                        path = file.absolutePath,
                        isDirectory = file.isDirectory,
                        size = if (file.isFile) file.length() else 0L,
                        lastModified = file.lastModified(),
                        extension = if (file.isFile) file.extension.lowercase() else ""
                    ))
                }
            results
        } catch (_: Exception) { emptyList() }
    }

    suspend fun getStorageInfo(): StorageInfo = withContext(Dispatchers.IO) {
        try {
            val root = File(Constants.ROOT_PATH)
            StorageInfo(
                totalSpace = root.totalSpace,
                freeSpace = root.freeSpace,
                usedSpace = root.totalSpace - root.freeSpace
            )
        } catch (_: Exception) {
            StorageInfo(0, 0, 0)
        }
    }

    suspend fun getRecentFiles(path: String, limit: Int = 50): List<FileItem> = withContext(Dispatchers.IO) {
        try {
            val dir = File(path)
            dir.walkTopDown()
                .maxDepth(3)
                .filter { it.isFile }
                .sortedByDescending { it.lastModified() }
                .take(limit)
                .map { file ->
                    FileItem(
                        name = file.name,
                        path = file.absolutePath,
                        isDirectory = false,
                        size = file.length(),
                        lastModified = file.lastModified(),
                        extension = file.extension.lowercase()
                    )
                }.toList()
        } catch (_: Exception) { emptyList() }
    }
}

data class StorageInfo(
    val totalSpace: Long,
    val freeSpace: Long,
    val usedSpace: Long
)
'''

# 11. data/repository/GeminiApi.kt
files[f"{BASE}/data/repository/GeminiApi.kt"] = '''package com.erople.mybasic.aidevtoolbox.data.repository

import com.erople.mybasic.aidevtoolbox.core.Constants
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

object GeminiApi {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    suspend fun sendMessage(
        message: String,
        history: List<Pair<String, String>> = emptyList(),
        model: String = "gemini-2.0-flash"
    ): String = withContext(Dispatchers.IO) {
        try {
            val apiKey = Constants.GEMINI_API_KEY
            val url = "https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=$apiKey"

            val contentsArray = JSONArray()
            for ((role, text) in history) {
                val content = JSONObject()
                content.put("role", if (role == "user") "user" else "model")
                val parts = JSONArray()
                parts.put(JSONObject().put("text", text))
                content.put("parts", parts)
                contentsArray.put(content)
            }

            val userContent = JSONObject()
            userContent.put("role", "user")
            val userParts = JSONArray()
            userParts.put(JSONObject().put("text", message))
            userContent.put("parts", userParts)
            contentsArray.put(userContent)

            val requestBody = JSONObject()
            requestBody.put("contents", contentsArray)

            val request = Request.Builder()
                .url(url)
                .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
                .build()

            val response = client.newCall(request).execute()
            val body = response.body?.string() ?: ""

            if (!response.isSuccessful) {
                return@withContext "API Error ${response.code}: $body"
            }

            val jsonResponse = JSONObject(body)
            val candidates = jsonResponse.getJSONArray("candidates")
            if (candidates.length() > 0) {
                val content = candidates.getJSONObject(0).getJSONObject("content")
                val parts = content.getJSONArray("parts")
                if (parts.length() > 0) {
                    return@withContext parts.getJSONObject(0).getString("text")
                }
            }
            "No response from AI"
        } catch (e: Exception) {
            "Error: ${e.message}"
        }
    }
}
'''

# 12. ui/ai/AIChatFragment.kt
files[f"{BASE}/ui/ai/AIChatFragment.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.ai

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.PopupMenu
import androidx.appcompat.app.AlertDialog
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.erople.mybasic.aidevtoolbox.R
import com.erople.mybasic.aidevtoolbox.core.BaseFragment
import com.erople.mybasic.aidevtoolbox.core.StreamState
import com.erople.mybasic.aidevtoolbox.core.copyToClipboard
import com.erople.mybasic.aidevtoolbox.core.dp
import com.erople.mybasic.aidevtoolbox.core.gone
import com.erople.mybasic.aidevtoolbox.core.visible
import com.erople.mybasic.aidevtoolbox.databinding.FragmentAiChatBinding

class AIChatFragment : BaseFragment() {
    private var _binding: FragmentAiChatBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: ChatViewModel
    private lateinit var chatAdapter: ChatAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentAiChatBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun setupViews(view: View) {
        viewModel = ViewModelProvider(this)[ChatViewModel::class.java]
        setupChat()
        setupInput()
        setupModelSelector()
    }

    override fun observeData() {
        viewModel.messages.observe(viewLifecycleOwner) { state ->
            handleState(state) { messages ->
                chatAdapter.submitList(messages)
                if (messages.isNotEmpty()) binding.recyclerChat.scrollToPosition(messages.size - 1)
                if (messages.isEmpty()) { binding.emptyState.visible(); binding.recyclerChat.gone() }
                else { binding.emptyState.gone(); binding.recyclerChat.visible() }
            }
        }
        viewModel.streamState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is StreamState.Streaming -> { binding.btnSend.gone(); binding.btnStop.visible() }
                else -> { binding.btnSend.visible(); binding.btnStop.gone() }
            }
        }
        viewModel.tokenCount.observe(viewLifecycleOwner) { count -> binding.tokenCounter.text = "$count tokens" }
    }

    private fun setupChat() {
        chatAdapter = ChatAdapter(
            onCopyClick = { text -> requireContext().copyToClipboard(text) },
            onRegenerate = { viewModel.regenerateLastResponse() },
            onEditPrompt = { id, text -> showEditDialog(id, text) }
        )
        binding.recyclerChat.apply { layoutManager = LinearLayoutManager(context).apply { stackFromEnd = true }; adapter = chatAdapter }
    }

    private fun setupInput() {
        binding.btnSend.setOnClickListener {
            val text = binding.inputField.text.toString().trim()
            if (text.isNotEmpty()) { viewModel.sendMessage(text); binding.inputField.text?.clear() }
        }
        binding.btnStop.setOnClickListener { viewModel.stopGeneration() }
        binding.btnNewChat.setOnClickListener { viewModel.newChat() }
        binding.btnModelSelector.setOnClickListener { showModelPopup(it) }
    }

    private fun setupModelSelector() { binding.btnModelSelector.text = "gemini-2.0-flash" }

    private fun showModelPopup(anchor: View) {
        val popup = PopupMenu(requireContext(), anchor)
        listOf("gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash").forEach { popup.menu.add(it) }
        popup.setOnMenuItemClickListener { item -> viewModel.selectModel(item.title.toString()); binding.btnModelSelector.text = item.title; true }
        popup.show()
    }

    private fun showEditDialog(messageId: String, currentText: String) {
        val input = EditText(requireContext()).apply { setText(currentText); setPadding(dp(32), dp(16), dp(32), dp(8)); minLines = 3 }
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog).setTitle("Edit Prompt").setView(input)
            .setPositiveButton("OK") { _, _ -> viewModel.editMessage(messageId, input.text.toString().trim()) }
            .setNegativeButton("Cancel", null).show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
'''

# 13. ui/ai/ChatAdapter.kt
files[f"{BASE}/ui/ai/ChatAdapter.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.ai

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.erople.mybasic.aidevtoolbox.R
import com.erople.mybasic.aidevtoolbox.data.model.ChatMessage
import com.erople.mybasic.aidevtoolbox.data.model.MessageRole

class ChatAdapter(
    private val onCopyClick: (String) -> Unit,
    private val onRegenerate: () -> Unit,
    private val onEditPrompt: (String, String) -> Unit
) : ListAdapter<ChatMessage, RecyclerView.ViewHolder>(ChatDiffCallback()) {

    companion object {
        const val TYPE_USER = 0
        const val TYPE_ASSISTANT = 1
    }

    override fun getItemViewType(position: Int) = when (getItem(position).role) {
        MessageRole.USER -> TYPE_USER
        else -> TYPE_ASSISTANT
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        return if (viewType == TYPE_USER) UserViewHolder(inflater.inflate(R.layout.item_chat_user, parent, false))
        else AssistantViewHolder(inflater.inflate(R.layout.item_chat_ai, parent, false))
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is UserViewHolder -> holder.bind(getItem(position))
            is AssistantViewHolder -> holder.bind(getItem(position))
        }
    }

    inner class UserViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val messageText: TextView = view.findViewById(R.id.message_text)
        private val editButton: ImageButton = view.findViewById(R.id.btn_edit)
        fun bind(msg: ChatMessage) { messageText.text = msg.content; editButton.setOnClickListener { onEditPrompt(msg.id, msg.content) } }
    }

    inner class AssistantViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val messageText: TextView = view.findViewById(R.id.message_text)
        private val copyButton: ImageButton = view.findViewById(R.id.btn_copy)
        private val regenerateButton: ImageButton = view.findViewById(R.id.btn_regenerate)
        private val streamingIndicator: View? = view.findViewById(R.id.streaming_indicator)
        fun bind(msg: ChatMessage) {
            messageText.text = msg.content
            streamingIndicator?.visibility = if (msg.isStreaming) View.VISIBLE else View.GONE
            copyButton.setOnClickListener { onCopyClick(msg.content) }
            regenerateButton.setOnClickListener { onRegenerate() }
        }
    }

    class ChatDiffCallback : DiffUtil.ItemCallback<ChatMessage>() {
        override fun areItemsTheSame(old: ChatMessage, new: ChatMessage) = old.id == new.id
        override fun areContentsTheSame(old: ChatMessage, new: ChatMessage) = old == new
    }
}
'''

# 14. ui/files/FilesFragment.kt
files[f"{BASE}/ui/files/FilesFragment.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.files

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import androidx.appcompat.app.AlertDialog
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.erople.mybasic.aidevtoolbox.R
import com.erople.mybasic.aidevtoolbox.core.BaseFragment
import com.erople.mybasic.aidevtoolbox.core.dp
import com.erople.mybasic.aidevtoolbox.core.formatFileSize
import com.erople.mybasic.aidevtoolbox.core.toast
import com.erople.mybasic.aidevtoolbox.data.model.FilterType
import com.erople.mybasic.aidevtoolbox.data.model.SortField
import com.erople.mybasic.aidevtoolbox.data.model.SortOrder
import com.erople.mybasic.aidevtoolbox.databinding.FragmentFilesBinding

class FilesFragment : BaseFragment() {
    private var _binding: FragmentFilesBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: FilesViewModel
    private lateinit var fileAdapter: FileAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentFilesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun setupViews(view: View) {
        viewModel = ViewModelProvider(this)[FilesViewModel::class.java]
        setupRecyclerView()
        setupSearch()
        setupFab()
        setupRetry { viewModel.loadFiles() }
    }

    override fun observeData() {
        viewModel.files.observe(viewLifecycleOwner) { state ->
            handleState(state) { files -> fileAdapter.submitList(files) }
        }
        viewModel.storageInfo.observe(viewLifecycleOwner) { info ->
            binding.storageText.text = "${info.usedSpace.formatFileSize()} of ${info.totalSpace.formatFileSize()} used"
        }
    }

    private fun setupRecyclerView() {
        fileAdapter = FileAdapter(
            onItemClick = { item ->
                if (item.isDirectory) viewModel.loadFiles(item.path)
                else toast("Opening: ${item.name}")
            },
            onItemLongClick = { item -> showFileActions(item) }
        )
        binding.fileList.apply { layoutManager = LinearLayoutManager(context); adapter = fileAdapter }
    }

    private fun setupSearch() {
        binding.searchInput.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val query = s?.toString() ?: ""
                if (query.length >= 2) viewModel.searchFiles(query)
            }
        })
    }

    private fun setupFab() {
        binding.fabAdd.setOnClickListener { showCreateFolderDialog() }
        binding.sortButton.setOnClickListener { showSortDialog() }
        binding.filterButton.setOnClickListener { showFilterDialog() }
    }

    fun showFileActions(item: com.erople.mybasic.aidevtoolbox.data.model.FileItem) {
        val actions = arrayOf("Info", "Rename", "Delete")
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle(item.name)
            .setItems(actions) { _, which ->
                when (which) {
                    0 -> toast("Name: ${item.name}\\nSize: ${item.sizeFormatted}\\nType: ${item.type}")
                    1 -> showRenameDialog(item)
                    2 -> confirmDelete(item)
                }
            }.show()
    }

    private fun showCreateFolderDialog() {
        val input = EditText(requireContext()).apply { hint = "Folder name"; setPadding(dp(32), dp(16), dp(32), dp(8)) }
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("Create Folder").setView(input)
            .setPositiveButton("OK") { _, _ ->
                val name = input.text.toString().trim()
                if (name.isNotEmpty()) { viewModel.createFolder(name); toast("Folder created") }
            }.setNegativeButton("Cancel", null).show()
    }

    private fun showRenameDialog(item: com.erople.mybasic.aidevtoolbox.data.model.FileItem) {
        val input = EditText(requireContext()).apply { setText(item.name); setPadding(dp(32), dp(16), dp(32), dp(8)) }
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("Rename").setView(input)
            .setPositiveButton("OK") { _, _ ->
                val newName = input.text.toString().trim()
                if (newName.isNotEmpty()) { viewModel.renameFile(item.path, newName); toast("Renamed") }
            }.setNegativeButton("Cancel", null).show()
    }

    private fun showSortDialog() {
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("Sort by")
            .setItems(arrayOf("Name", "Size", "Date", "Type")) { _, which ->
                val field = SortField.entries[which]
                val order = if (viewModel.getSortOrder() == SortOrder.ASCENDING) SortOrder.DESCENDING else SortOrder.ASCENDING
                viewModel.setSort(field, order)
            }.show()
    }

    private fun showFilterDialog() {
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("Filter")
            .setItems(arrayOf("All", "Images", "Videos", "Audio", "Docs", "Code", "Archives")) { _, which ->
                viewModel.setFilter(FilterType.entries[which])
            }.show()
    }

    private fun confirmDelete(item: com.erople.mybasic.aidevtoolbox.data.model.FileItem) {
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("Delete").setMessage("Delete ${item.name}?")
            .setPositiveButton("Delete") { _, _ -> viewModel.deleteFile(item.path); toast("Deleted") }
            .setNegativeButton("Cancel", null).show()
    }

    fun refreshFiles() { viewModel.loadFiles() }
    fun scrollToTop() { binding.fileList.smoothScrollToPosition(0) }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
'''

# 15. ui/files/FilesViewModel.kt
files[f"{BASE}/ui/files/FilesViewModel.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.files

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.erople.mybasic.aidevtoolbox.core.ViewState
import com.erople.mybasic.aidevtoolbox.data.model.*
import com.erople.mybasic.aidevtoolbox.data.repository.FileRepository
import com.erople.mybasic.aidevtoolbox.data.repository.StorageInfo
import kotlinx.coroutines.launch

class FilesViewModel : ViewModel() {
    private val repository = FileRepository()

    private val _files = MutableLiveData<ViewState<List<FileItem>>>()
    val files: LiveData<ViewState<List<FileItem>>> = _files

    private val _storageInfo = MutableLiveData<StorageInfo>()
    val storageInfo: LiveData<StorageInfo> = _storageInfo

    private val _searchResults = MutableLiveData<ViewState<List<FileItem>>>()
    val searchResults: LiveData<ViewState<List<FileItem>>> = _searchResults

    private var currentPath = "/storage/emulated/0"
    private var sortField = SortField.NAME
    private var sortOrder = SortOrder.ASCENDING
    private var filterType = FilterType.ALL
    private var showHidden = false

    fun loadFiles(path: String = currentPath) {
        currentPath = path
        _files.value = ViewState.Loading
        viewModelScope.launch {
            try {
                val fileList = repository.getFiles(path, sortField, sortOrder, filterType, showHidden)
                if (fileList.isEmpty()) {
                    _files.postValue(ViewState.Empty)
                } else {
                    _files.postValue(ViewState.Success(fileList))
                }
                _storageInfo.postValue(repository.getStorageInfo())
            } catch (e: Exception) {
                _files.postValue(ViewState.Error(e.message ?: "Failed to load files"))
            }
        }
    }

    fun searchFiles(query: String) {
        if (query.length < 2) return
        _searchResults.value = ViewState.Loading
        viewModelScope.launch {
            val results = repository.searchFiles(currentPath, query)
            _searchResults.postValue(
                if (results.isEmpty()) ViewState.Empty
                else ViewState.Success(results)
            )
        }
    }

    fun setSort(field: SortField, order: SortOrder) {
        sortField = field
        sortOrder = order
        loadFiles()
    }

    fun setFilter(type: FilterType) {
        filterType = type
        loadFiles()
    }

    fun toggleHidden() {
        showHidden = !showHidden
        loadFiles()
    }

    fun createFolder(name: String) {
        viewModelScope.launch {
            if (repository.createFolder(currentPath, name)) {
                loadFiles()
            }
        }
    }

    fun deleteFile(path: String) {
        viewModelScope.launch {
            if (repository.deleteFile(path)) loadFiles()
        }
    }

    fun renameFile(path: String, newName: String) {
        viewModelScope.launch {
            if (repository.renameFile(path, newName)) loadFiles()
        }
    }

    fun copyFile(source: String, destDir: String) {
        viewModelScope.launch {
            repository.copyFile(source, destDir)
            loadFiles()
        }
    }

    fun moveFile(source: String, destDir: String) {
        viewModelScope.launch {
            repository.moveFile(source, destDir)
            loadFiles()
        }
    }

    fun getCurrentPath(): String = currentPath
    fun getSortField(): SortField = sortField
    fun getSortOrder(): SortOrder = sortOrder
    fun getFilterType(): FilterType = filterType
}
'''

# 16. ui/files/FileAdapter.kt
files[f"{BASE}/ui/files/FileAdapter.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.files

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.erople.mybasic.aidevtoolbox.R
import com.erople.mybasic.aidevtoolbox.core.color
import com.erople.mybasic.aidevtoolbox.core.formatDate
import com.erople.mybasic.aidevtoolbox.data.model.FileItem
import com.erople.mybasic.aidevtoolbox.data.model.FileType

class FileAdapter(
    private val onItemClick: (FileItem) -> Unit,
    private val onItemLongClick: (FileItem) -> Unit
) : ListAdapter<FileItem, FileAdapter.FileViewHolder>(FileDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FileViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_file, parent, false)
        return FileViewHolder(view)
    }

    override fun onBindViewHolder(holder: FileViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class FileViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val iconView: ImageView = itemView.findViewById(R.id.file_icon)
        private val nameText: TextView = itemView.findViewById(R.id.file_name)
        private val infoText: TextView = itemView.findViewById(R.id.file_info)
        private val sizeText: TextView = itemView.findViewById(R.id.file_size)
        private val dateText: TextView = itemView.findViewById(R.id.file_date)

        fun bind(item: FileItem) {
            nameText.text = item.name
            infoText.text = if (item.isDirectory) "Folder" else item.extension.uppercase()
            sizeText.text = item.sizeFormatted
            dateText.text = item.lastModified.formatDate()

            val (iconRes, colorRes) = when (item.type) {
                FileType.FOLDER -> Pair(R.drawable.ic_folder, R.color.file_folder)
                FileType.IMAGE -> Pair(R.drawable.ic_file, R.color.file_image)
                FileType.VIDEO -> Pair(R.drawable.ic_file, R.color.file_video)
                FileType.AUDIO -> Pair(R.drawable.ic_file, R.color.file_audio)
                FileType.CODE -> Pair(R.drawable.ic_file, R.color.file_code)
                FileType.DOCUMENT -> Pair(R.drawable.ic_file, R.color.file_document)
                FileType.ARCHIVE -> Pair(R.drawable.ic_file, R.color.file_archive)
                else -> Pair(R.drawable.ic_file, R.color.file_default)
            }
            iconView.setImageResource(iconRes)
            iconView.setColorFilter(ContextCompat.getColor(itemView.context, colorRes))

            itemView.setOnClickListener { onItemClick(item) }
            itemView.setOnLongClickListener {
                onItemLongClick(item)
                true
            }
        }
    }

    class FileDiffCallback : DiffUtil.ItemCallback<FileItem>() {
        override fun areItemsTheSame(old: FileItem, new: FileItem) = old.path == new.path
        override fun areContentsTheSame(old: FileItem, new: FileItem) = old == new
    }
}
'''

# 17. ui/tools/ToolAdapter.kt
files[f"{BASE}/ui/tools/ToolAdapter.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.tools

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.erople.mybasic.aidevtoolbox.R
import com.erople.mybasic.aidevtoolbox.data.model.ToolItem

class ToolAdapter(
    private val tools: List<ToolItem>,
    private val onClick: (ToolItem) -> Unit
) : RecyclerView.Adapter<ToolAdapter.ToolViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ToolViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_tool, parent, false)
        return ToolViewHolder(view)
    }

    override fun getItemCount() = tools.size

    override fun onBindViewHolder(holder: ToolViewHolder, position: Int) {
        holder.bind(tools[position])
    }

    inner class ToolViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val icon: ImageView = view.findViewById(R.id.tool_icon)
        private val name: TextView = view.findViewById(R.id.tool_name)
        private val desc: TextView = view.findViewById(R.id.tool_desc)

        fun bind(tool: ToolItem) {
            name.text = tool.name
            desc.text = tool.description
            icon.setImageResource(tool.iconRes)
            itemView.setOnClickListener { onClick(tool) }
        }
    }
}
'''

# 18. ui/recent/RecentFragment.kt
files[f"{BASE}/ui/recent/RecentFragment.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.recent

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.erople.mybasic.aidevtoolbox.core.BaseFragment
import com.erople.mybasic.aidevtoolbox.core.Constants
import com.erople.mybasic.aidevtoolbox.data.model.FileItem
import com.erople.mybasic.aidevtoolbox.data.repository.FileRepository
import com.erople.mybasic.aidevtoolbox.databinding.FragmentRecentBinding
import com.erople.mybasic.aidevtoolbox.ui.files.FileAdapter
import kotlinx.coroutines.launch

class RecentFragment : BaseFragment() {
    private var _binding: FragmentRecentBinding? = null
    private val binding get() = _binding!!
    private val repository = FileRepository()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentRecentBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun setupViews(view: View) {
        setupRetry { loadRecentFiles() }
    }

    override fun observeData() {
        loadRecentFiles()
    }

    private fun loadRecentFiles() {
        showLoading()
        lifecycleScope.launch {
            try {
                val files = repository.getRecentFiles(Constants.ROOT_PATH, 50)
                if (files.isEmpty()) {
                    showEmpty()
                } else {
                    showContent()
                    val adapter = FileAdapter(
                        onItemClick = { },
                        onItemLongClick = { }
                    )
                    binding.recyclerRecent.layoutManager = LinearLayoutManager(context)
                    binding.recyclerRecent.adapter = adapter
                    adapter.submitList(files)
                }
            } catch (e: Exception) {
                showError(e.message ?: "Failed to load recent files")
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
'''

# 19. ui/profile/ProfileFragment.kt
files[f"{BASE}/ui/profile/ProfileFragment.kt"] = '''package com.erople.mybasic.aidevtoolbox.ui.profile

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.appcompat.app.AlertDialog
import com.erople.mybasic.aidevtoolbox.R
import com.erople.mybasic.aidevtoolbox.core.*
import com.erople.mybasic.aidevtoolbox.databinding.FragmentProfileBinding

class ProfileFragment : BaseFragment() {
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun setupViews(view: View) {
        showContent()

        binding.btnAppearance.setOnClickListener {
            ThemeManager.toggleTheme(requireActivity())
            toast("Theme toggled")
        }

        binding.btnNotifications.setOnClickListener {
            toast("Notification settings coming soon")
        }

        binding.btnSecurity.setOnClickListener {
            toast("Security settings coming soon")
        }

        binding.btnBackup.setOnClickListener {
            toast("Backup & sync coming soon")
        }

        binding.btnAbout.setOnClickListener {
            AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
                .setTitle("About DevToolBox")
                .setMessage("Version: ${Constants.APP_VERSION}\\n" +
                    "Build: ${Constants.APP_VERSION_CODE}\\n\\n" +
                    "A premium developer toolbox with AI, file management, and dev tools.\\n\\n" +
                    "License: MIT")
                .setPositiveButton("OK", null)
                .show()
        }

        binding.btnClearCache.setOnClickListener {
            CacheManager.clearAll()
            toast("Cache cleared")
        }

        binding.btnErrorLogs.setOnClickListener {
            val logs = ErrorHandler.getErrorLogs()
            AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
                .setTitle("Error Logs")
                .setMessage(logs.take(2000))
                .setPositiveButton("Clear") { _, _ ->
                    ErrorHandler.clearErrorLogs()
                    toast("Logs cleared")
                }
                .setNegativeButton("Close", null)
                .show()
        }
    }

    override fun observeData() {}

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
'''

# 20. util/SecurityUtils.kt
files[f"{BASE}/util/SecurityUtils.kt"] = '''package com.erople.mybasic.aidevtoolbox.util

import java.io.File

object SecurityUtils {
    fun canRead(path: String): Boolean {
        return try { File(path).exists() && File(path).canRead() } catch (_: Exception) { false }
    }

    fun canWrite(path: String): Boolean {
        return try { File(path).exists() && File(path).canWrite() } catch (_: Exception) { false }
    }

    fun sanitizeFileName(name: String): String {
        return name.replace("[^a-zA-Z0-9._-]".toRegex(), "_").replace("..", "_").trim('_')
    }

    fun isValidPath(path: String): Boolean {
        return path.isNotEmpty() && !path.contains("..") && path.startsWith("/")
    }

    fun calculateChecksum(file: File, algorithm: String = "SHA-256"): String {
        return try {
            val digest = java.security.MessageDigest.getInstance(algorithm)
            file.inputStream().use { input ->
                val buffer = ByteArray(8192)
                var read: Int
                while (input.read(buffer).also { read = it } != -1) {
                    digest.update(buffer, 0, read)
                }
            }
            digest.digest().joinToString("") { "%02x".format(it) }
        } catch (_: Exception) { "" }
    }
}
'''

# 21. util/ShareUtils.kt
files[f"{BASE}/util/ShareUtils.kt"] = '''package com.erople.mybasic.aidevtoolbox.util

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.webkit.MimeTypeMap
import androidx.core.content.FileProvider
import java.io.File

object ShareUtils {

    fun shareFile(context: Context, file: File) {
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.provider", file)
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = getMimeType(file)
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(intent, "Share via"))
    }

    fun shareText(context: Context, text: String, subject: String = "") {
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, text)
            if (subject.isNotEmpty()) putExtra(Intent.EXTRA_SUBJECT, subject)
        }
        context.startActivity(Intent.createChooser(intent, "Share via"))
    }

    fun shareMultiple(context: Context, files: List<File>) {
        val uris = files.map { file ->
            FileProvider.getUriForFile(context, "${context.packageName}.provider", file)
        }
        val intent = Intent(Intent.ACTION_SEND_MULTIPLE).apply {
            type = "*/*"
            putParcelableArrayListExtra(Intent.EXTRA_STREAM, ArrayList(uris))
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(intent, "Share via"))
    }

    fun exportToFile(context: Context, content: String, fileName: String, mimeType: String = "text/plain"): Uri? {
        return try {
            val file = File(context.cacheDir, fileName)
            file.writeText(content)
            FileProvider.getUriForFile(context, "${context.packageName}.provider", file)
        } catch (_: Exception) { null }
    }

    fun getMimeType(file: File): String {
        val ext = file.extension.lowercase()
        return MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext) ?: "*/*"
    }
}
'''

# 22. MainActivity.kt
files[f"{BASE}/MainActivity.kt"] = '''package com.erople.mybasic.aidevtoolbox

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.Settings
import android.view.View
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import androidx.fragment.app.Fragment
import com.erople.mybasic.aidevtoolbox.core.ThemeManager
import com.erople.mybasic.aidevtoolbox.core.toast
import com.erople.mybasic.aidevtoolbox.databinding.ActivityMainBinding
import com.erople.mybasic.aidevtoolbox.ui.ai.AIChatFragment
import com.erople.mybasic.aidevtoolbox.ui.editor.CodeEditorFragment
import com.erople.mybasic.aidevtoolbox.ui.files.FilesFragment
import com.erople.mybasic.aidevtoolbox.ui.profile.ProfileFragment
import com.erople.mybasic.aidevtoolbox.ui.recent.RecentFragment
import com.erople.mybasic.aidevtoolbox.ui.tools.ToolsFragment

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private var currentFragment: Fragment? = null
    private var activeTabId: Int = R.id.nav_files
    private val fragments = mutableMapOf<Int, Fragment>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setupNavigation()
        checkPermissions()
        if (savedInstanceState == null) {
            binding.bottomNav.selectedItemId = R.id.nav_files
        }
    }

    private fun setupNavigation() {
        binding.bottomNav.setOnItemSelectedListener { item ->
            navigateTo(item.itemId)
            true
        }
    }

    private fun navigateTo(itemId: Int) {
        val targetFragment = fragments.getOrPut(itemId) {
            when (itemId) {
                R.id.nav_files -> FilesFragment()
                R.id.nav_ai -> AIChatFragment()
                R.id.nav_tools -> ToolsFragment()
                R.id.nav_recent -> RecentFragment()
                R.id.nav_profile -> ProfileFragment()
                else -> FilesFragment()
            }
        }
        val transaction = supportFragmentManager.beginTransaction()
        currentFragment?.let { transaction.hide(it) }
        if (targetFragment.isAdded) {
            transaction.show(targetFragment)
        } else {
            transaction.add(R.id.container, targetFragment)
        }
        transaction.setReorderingAllowed(true)
        transaction.commit()
        currentFragment = targetFragment
        activeTabId = itemId
    }

    private fun checkPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                AlertDialog.Builder(this, R.style.PremiumDialog)
                    .setTitle("Storage Permission")
                    .setMessage("DevToolBox needs access to manage all files.")
                    .setPositiveButton("Grant") { _, _ ->
                        val intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                        intent.data = Uri.parse("package:$packageName")
                        startActivityForResult(intent, 1001)
                    }
                    .setNegativeButton("Cancel", null)
                    .show()
            }
        } else {
            val perms = arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE)
            val needed = perms.filter { ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }
            if (needed.isNotEmpty()) ActivityCompat.requestPermissions(this, needed.toTypedArray(), 1002)
        }
    }

    override fun onBackPressed() {
        if (supportFragmentManager.backStackEntryCount > 0) {
            supportFragmentManager.popBackStack()
        } else if (activeTabId != R.id.nav_files) {
            binding.bottomNav.selectedItemId = R.id.nav_files
        } else {
            super.onBackPressed()
        }
    }

    fun openCodeEditor(filePath: String) {
        val fragment = CodeEditorFragment.newInstance(filePath)
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, fragment)
            .addToBackStack("code_editor")
            .commit()
        binding.bottomNav.visibility = View.GONE
    }

    fun showBottomNav() { binding.bottomNav.visibility = View.VISIBLE }
    fun hideBottomNav() { binding.bottomNav.visibility = View.GONE }
}
'''

print(f"=== Uploading {len(files)} files ===")
success = 0
failed = 0

for path, content in files.items():
    filename = path.split("/")[-1]
    print(f"\n[{success+failed+1}/22] {filename}...")
    try:
        ok = upload(content, path)
        if ok:
            size = verify(path)
            if size > 0:
                success += 1
            else:
                print(f"  ⚠️  Empty after upload!")
                failed += 1
        else:
            print(f"  ❌ Upload failed")
            failed += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed += 1

print(f"\n=== DONE: {success} success, {failed} failed out of {len(files)} files ===")
