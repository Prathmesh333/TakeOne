"""
Quick GPU Check Script
Run this to verify PyTorch can see your GPU
"""
import torch

print("="*60)
print("GPU DETECTION CHECK")
print("="*60)

print(f"\nPyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"GPU Count: {torch.cuda.device_count()}")
    print(f"Current GPU: {torch.cuda.current_device()}")
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print("\n✅ GPU READY - Your system will use GPU acceleration!")
else:
    print("\n❌ GPU NOT DETECTED")
    print("Possible reasons:")
    print("  1. PyTorch CPU-only version installed")
    print("  2. CUDA drivers not installed")
    print("  3. Incompatible CUDA version")
    print("\nTo fix: Run install_pytorch_cuda.bat")

print("="*60)

# Test YOLO
print("\nTesting YOLO GPU support...")
try:
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt")
    
    if torch.cuda.is_available():
        model.to('cuda')
        print("✅ YOLO can use GPU")
    else:
        print("⚠️ YOLO will use CPU (slower)")
except Exception as e:
    print(f"❌ YOLO test failed: {e}")

print("="*60)
