import { useRef, useState } from "react";
import { Button } from "./ui/button";
import { Upload, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { predictAnomalies } from "../lib/api";
import { transformBackendAnomalyToSession } from "../lib/transformers";
import type { EVSession } from "./EVDashboard";

interface FileUploadProps {
  onFileUpload: (sessions: EVSession[]) => void;
}

export function FileUpload({ onFileUpload }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error("Please upload a CSV file");
      return;
    }

    setIsUploading(true);

    try {
      const response = await predictAnomalies(file);
      const sessions = response.anomalies.map(transformBackendAnomalyToSession);
      onFileUpload(sessions);

      toast.success(
        `Analyzed ${response.total_sessions} sessions. Found ${response.anomalies_found} anomalies.`,
        {
          description: `File: ${response.filename}`,
          duration: 5000,
        }
      );
    } catch (error: unknown) {
      console.error('Upload error:', error);
      const axiosError = error as { response?: { data?: { detail?: string } }; request?: unknown; message?: string };

      const isTimeout = (error as { code?: string }).code === 'ECONNABORTED';
      if (axiosError.response) {
        toast.error(
          `Upload failed: ${axiosError.response.data?.detail || 'Server error'}`
        );
      } else if (isTimeout) {
        toast.error('Upload timed out', {
          description: 'The file is too large or the server is under load. Try a smaller file (max 20,000 rows).',
        });
      } else if (axiosError.request) {
        toast.error('Cannot reach server', {
          description: 'The backend may be starting up — wait a few seconds and try again.',
        });
      } else {
        toast.error('Upload failed', { description: axiosError.message });
      }
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        className="hidden"
        disabled={isUploading}
      />
      <Button
        onClick={() => fileInputRef.current?.click()}
        className="bg-blue-600 hover:bg-blue-700"
        disabled={isUploading}
      >
        {isUploading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Upload className="w-4 h-4 mr-2" />
            Upload CSV
          </>
        )}
      </Button>
    </>
  );
}
