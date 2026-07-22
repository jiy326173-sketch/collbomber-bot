android.content.Intent
import android.net.Uri
import andrle.ViewModelProvider
import androidx.recyclerview.widget.t() {
    private var _binding: FragmentFilesBinding? = nView(inflater: LayoutInflater, container: ViewGroup?, savs(view: View) {
        viewModel = ViewModelProvider(thish.setOnRefreshListener { refreshFiles() }
    }

    oveiles)
                updatePathBar()
            }
     rmatFileSize()} used"
        }
    }

    private fun sem.path)
                } else {
                    open= fileAdapter
        }
    }

    private fun setupSearcoreTextChanged(s: CharSequence?, start: Int, count: Int,                searchJob?.cancel()
                search?.toString() ?: ""
                            if (query.       }
                }
                java.util.TimelderDialog() }
        binding.sortButton.setOnClickListeles(path)
    }

    private fun openFile(item: FileItem)  try {
                val intent = Intent(Intent.ACTION(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                sem: FileItem) {
        val actions = arrayOf("Info", "Re         .setTitle(item.name)
            .setItems(actio("Copy: select destination folder")
                    3    .show()
    }

    private fun showFileInfo(item: Fil.type}")
            appendLine("Size: \${item.sizeFormatItem) {
        try {
            val file = File(item.pat, "Share via"))
        } catch (_: Exception) {
                   .setTitle("Delete")
            .setMessage("string.file_deleted)
            }
            .setNegati    fun scrollToTop() {
        binding.fileList.smoothSc