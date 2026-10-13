import React, { useState } from 'react';
import { api } from '../services/api';
import { ImportPreviewItem, ImportResponse } from '../types';
import { X, Upload, CheckCircle2, AlertTriangle, FileText, Check } from 'lucide-react';

interface CSVImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  adminKey: string;
  onImportComplete: () => void;
}

export const CSVImportModal: React.FC<CSVImportModalProps> = ({
  isOpen,
  onClose,
  adminKey,
  onImportComplete,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewRows, setPreviewRows] = useState<ImportPreviewItem[] | null>(null);
  const [totalRows, setTotalRows] = useState(0);
  const [importSummary, setImportSummary] = useState<ImportResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setSelectedFile(file);
    setErrorMessage(null);
    setImportSummary(null);
    setIsUploading(true);

    try {
      // Preview import
      const res = await api.previewImport(file, adminKey);
      setPreviewRows(res.preview);
      setTotalRows(res.total_rows);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to preview CSV file.');
      setPreviewRows(null);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCommit = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setErrorMessage(null);

    try {
      const res = await api.commitImport(selectedFile, adminKey);
      setImportSummary(res);
      onImportComplete();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to import CSV records.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewRows(null);
    setImportSummary(null);
    setErrorMessage(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-2xl bg-white dark:bg-library-darkCard rounded-3xl shadow-2xl border border-library-border dark:border-library-darkBorder overflow-hidden z-10 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-library-border dark:border-library-darkBorder flex items-center justify-between bg-slate-50 dark:bg-slate-900">
          <div className="flex items-center gap-2">
            <Upload className="w-5 h-5 text-emerald-600" />
            <h3 className="font-serif text-xl font-bold text-slate-900 dark:text-white">
              Import Catalogue Records from CSV
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1">
          {errorMessage && (
            <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Import Summary Results */}
          {importSummary ? (
            <div className="p-6 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-emerald-600 text-white flex items-center justify-center mx-auto">
                <Check className="w-6 h-6" />
              </div>
              <h4 className="font-serif text-xl font-bold text-emerald-900 dark:text-emerald-200">
                Import Process Completed
              </h4>

              <div className="grid grid-cols-3 gap-3 text-center pt-2">
                <div className="p-3 bg-white dark:bg-slate-900 rounded-xl border border-emerald-200 dark:border-emerald-800">
                  <span className="text-xs text-slate-400 block">Successfully Added</span>
                  <span className="text-xl font-bold text-emerald-600">{importSummary.imported}</span>
                </div>
                <div className="p-3 bg-white dark:bg-slate-900 rounded-xl border border-amber-200 dark:border-amber-800">
                  <span className="text-xs text-slate-400 block">Duplicates Skipped</span>
                  <span className="text-xl font-bold text-amber-600">
                    {importSummary.skipped_duplicates}
                  </span>
                </div>
                <div className="p-3 bg-white dark:bg-slate-900 rounded-xl border border-rose-200 dark:border-rose-800">
                  <span className="text-xs text-slate-400 block">Failed Validation</span>
                  <span className="text-xl font-bold text-rose-600">
                    {importSummary.failed_validation}
                  </span>
                </div>
              </div>

              {importSummary.errors.length > 0 && (
                <div className="text-left text-xs bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800 max-h-32 overflow-y-auto">
                  <span className="font-semibold block mb-1 text-slate-600 dark:text-slate-400">
                    Import Warnings:
                  </span>
                  {importSummary.errors.map((err, i) => (
                    <p key={i} className="text-rose-600 dark:text-rose-400 font-mono text-[11px]">
                      • {err}
                    </p>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <>
              {/* File Selector Dropzone */}
              {!selectedFile ? (
                <div className="border-2 border-dashed border-slate-200 dark:border-slate-700 hover:border-emerald-500 rounded-2xl p-8 text-center cursor-pointer transition-colors">
                  <input
                    type="file"
                    accept=".csv"
                    id="csv-file-input"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <label htmlFor="csv-file-input" className="cursor-pointer">
                    <FileText className="w-10 h-10 text-slate-400 mx-auto mb-3" />
                    <span className="font-medium text-slate-800 dark:text-slate-200 block text-sm">
                      Click to choose a CSV file or drag and drop
                    </span>
                    <span className="text-xs text-slate-400 block mt-1">
                      Expected columns: title, author, isbn, category, shelf_location, total_copies, available_copies
                    </span>
                  </label>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-emerald-600" />
                      <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                        {selectedFile.name}
                      </span>
                      <span className="text-xs text-slate-400">
                        ({(selectedFile.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={handleReset}
                      className="text-xs text-slate-500 hover:text-rose-600 font-medium"
                    >
                      Change File
                    </button>
                  </div>

                  {/* Preview Table */}
                  {previewRows && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <span>Previewing first {previewRows.length} rows of {totalRows} total rows</span>
                      </div>

                      <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden max-h-56 overflow-y-auto">
                        <table className="w-full text-xs text-left">
                          <thead className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-semibold sticky top-0">
                            <tr>
                              <th className="p-2">Row</th>
                              <th className="p-2">Title</th>
                              <th className="p-2">Author</th>
                              <th className="p-2">Copies</th>
                              <th className="p-2">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {previewRows.map((r) => (
                              <tr
                                key={r.row}
                                className={r.is_valid ? 'bg-white dark:bg-slate-900' : 'bg-rose-50/50 dark:bg-rose-950/20'}
                              >
                                <td className="p-2 font-mono">{r.row}</td>
                                <td className="p-2 font-medium max-w-xs truncate">{r.title}</td>
                                <td className="p-2 text-slate-500 truncate">{r.author || '—'}</td>
                                <td className="p-2">
                                  {r.available_copies}/{r.total_copies}
                                </td>
                                <td className="p-2">
                                  {r.is_valid ? (
                                    <span className="text-emerald-600 flex items-center gap-1 font-semibold">
                                      <CheckCircle2 className="w-3 h-3" /> Valid
                                    </span>
                                  ) : (
                                    <span className="text-rose-600 font-semibold truncate block" title={r.errors.join(', ')}>
                                      {r.errors[0] || 'Error'}
                                    </span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3 bg-slate-50 dark:bg-slate-900">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold hover:bg-slate-300 transition-colors"
          >
            {importSummary ? 'Done' : 'Cancel'}
          </button>

          {selectedFile && !importSummary && (
            <button
              onClick={handleCommit}
              disabled={isUploading}
              className="px-6 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-500 disabled:opacity-50 transition-colors shadow-sm flex items-center gap-2"
            >
              {isUploading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5" />
                  <span>Confirm & Import Valid Records</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
