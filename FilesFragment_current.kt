package com.erople.mybasic.aidevtoolbox.ui.files

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.core.content.FileProvider
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.erople.mybasic.aidevtoolbox.R
import com.erople.mybasic.aidevtoolbox.core.*
import com.erople.mybasic.aidevtoolbox.data.model.*
import com.erople.mybasic.aidevtoolbox.databinding.FragmentFilesBinding
import java.io.File

class FilesFragment : BaseFragment() {
    private var _binding: FragmentFilesBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: FilesViewModel
    private lateinit var fileAdapter: FileAdapter
    private val pathHistory = mutableListOf<String>()

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
        binding.swipeRefresh.setOnRefreshListener { refreshFiles() }
    }

    override fun observeData() {
        viewModel.files.observe(viewLifecycleOwner) { state ->
            handleState(state) { files ->
                fileAdapter.submitList(files)
                updatePathBar()
            }
        }
        viewModel.storageInfo.observe(viewLifecycleOwner) { info ->
            binding.storageText.text = "${info.usedSpace.formatFileSize()} of ${info.totalSpace.formatFileSize()} used"
        }
    }

    private fun setupRecyclerView() {
        fileAdapter = FileAdapter(
            onItemClick = { item ->
                if (item.isDirectory) {
                    navigateToFolder(item.path)
                } else {
                    openFile(item)
                }
            },
            onItemLongClick = { item -> showFileActions(item) }
        )
        binding.fileList.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = fileAdapter
        }
    }

    private fun setupSearch() {
        binding.searchInput.addTextChangedListener(object : TextWatcher {
            private var searchJob: java.util.TimerTask? = null
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                searchJob?.cancel()
                searchJob = object : java.util.TimerTask() {
                    override fun run() {
                        activity?.runOnUiThread {
                            val query = s?.toString() ?: ""
                            if (query.length >= Constants.MIN_SEARCH_LENGTH) {
                                viewModel.searchFiles(query)
                            }
                        }
                    }
                }
                java.util.Timer().schedule(searchJob, Constants.SEARCH_DEBOUNCE_MS)
            }
        })
    }

    private fun setupFab() {
        binding.fabAdd.setOnClickListener { showCreateFolderDialog() }
        binding.sortButton.setOnClickListener { showSortDialog() }
        binding.filterButton.setOnClickListener { showFilterDialog() }
    }

    private fun navigateToFolder(path: String) {
        pathHistory.add(viewModel.getCurrentPath())
        viewModel.loadFiles(path)
    }

    private fun openFile(item: FileItem) {
        if (item.type == FileType.CODE) {
            (activity as? com.erople.mybasic.aidevtoolbox.MainActivity)?.openCodeEditor(item.path)
        } else {
            try {
                val intent = Intent(Intent.ACTION_VIEW)
                val uri = FileProvider.getUriForFile(requireContext(), "${requireContext().packageName}.provider", File(item.path))
                intent.setDataAndType(uri, item.mimeType)
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                startActivity(intent)
            } catch (_: Exception) {
                toast("No app found to open this file")
            }
        }
    }

    fun showFileActions(item: FileItem) {
        val actions = arrayOf("Info", "Rename", "Copy", "Move", "Share", "Delete")
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle(item.name)
            .setItems(actions) { _, which ->
                when (which) {
                    0 -> showFileInfo(item)
                    1 -> showRenameDialog(item)
                    2 -> toast("Copy: select destination folder")
                    3 -> toast("Move: select destination folder")
                    4 -> shareFile(item)
                    5 -> confirmDelete(item)
                }
            }
            .show()
    }

    private fun showFileInfo(item: FileItem) {
        val info = buildString {
            appendLine("Name: \${item.name}")
            appendLine("Path: \${item.path}")
            appendLine("Type: \${item.type}")
            appendLine("Size: \${item.sizeFormatted}")
            appendLine("Modified: \${item.lastModified.formatFullDate()}")
            appendLine("Extension: \${item.extension.ifEmpty { "none" }}")
        }
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("File Info")
            .setMessage(info)
            .setPositiveButton("OK", null)
            .show()
    }

    private fun showCreateFolderDialog() {
        val input = EditText(requireContext()).apply {
            hint = getString(R.string.folder_name_hint)
            setPadding(dp(32), dp(16), dp(32), dp(8))
        }
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle(R.string.create_folder)
            .setView(input)
            .setPositiveButton(R.string.ok) { _, _ ->
                val name = input.text.toString().trim()
                if (name.isNotEmpty()) {
                    viewModel.createFolder(name)
                    toast(R.string.folder_created)
                }
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
    }

    private fun showRenameDialog(item: FileItem) {
        val input = EditText(requireContext()).apply {
            setText(item.name)
            setPadding(dp(32), dp(16), dp(32), dp(8))
        }
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle(R.string.rename)
            .setView(input)
            .setPositiveButton(R.string.ok) { _, _ ->
                val newName = input.text.toString().trim()
                if (newName.isNotEmpty()) {
                    viewModel.renameFile(item.path, newName)
                    toast(R.string.file_renamed)
                }
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
    }

    private fun showSortDialog() {
        val options = arrayOf("Name", "Size", "Date", "Type")
        val orders = arrayOf("Ascending", "Descending")
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle(R.string.sort_by)
            .setItems(options) { _, which ->
                val field = SortField.entries[which]
                val currentOrder = viewModel.getSortOrder()
                viewModel.setSort(field, currentOrder)
            }
            .setNeutralButton("Toggle Order") { _, _ ->
                val newOrder = if (viewModel.getSortOrder() == SortOrder.ASCENDING) SortOrder.DESCENDING else SortOrder.ASCENDING
                viewModel.setSort(viewModel.getSortField(), newOrder)
            }
            .show()
    }

    private fun showFilterDialog() {
        val options = arrayOf("All", "Images", "Videos", "Audio", "Documents", "Code", "Archives")
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("Filter")
            .setItems(options) { _, which ->
                viewModel.setFilter(FilterType.entries[which])
            }
            .show()
    }

    private fun shareFile(item: FileItem) {
        try {
            val file = File(item.path)
            val uri = FileProvider.getUriForFile(requireContext(), "${requireContext().packageName}.provider", file)
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = item.mimeType
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(intent, "Share via"))
        } catch (_: Exception) {
            toast("Cannot share this file")
        }
    }

    private fun confirmDelete(item: FileItem) {
        AlertDialog.Builder(requireContext(), R.style.PremiumDialog)
            .setTitle("Delete")
            .setMessage("Delete \${item.name}?\nThis cannot be undone.")
            .setPositiveButton("Delete") { _, _ ->
                viewModel.deleteFile(item.path)
                toast(R.string.file_deleted)
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
    }

    fun refreshFiles() {
        binding.swipeRefresh.isRefreshing = false
        viewModel.loadFiles()
    }

    fun scrollToTop() {
        binding.fileList.smoothScrollToPosition(0)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}