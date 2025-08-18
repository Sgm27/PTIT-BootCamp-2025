"""
Test Android App Build
Checks if Android app can be built and run with memoir features
"""
import os
import subprocess
import sys
from pathlib import Path

def check_android_project():
    """Check Android project structure"""
    print("🔍 Checking Android project structure...")
    
    android_path = Path("GeminiLiveDemo")
    if not android_path.exists():
        print("❌ Android project not found at GeminiLiveDemo/")
        return False
    
    # Check key files
    key_files = [
        "app/build.gradle.kts",
        "app/src/main/AndroidManifest.xml",
        "app/src/main/java/com/example/geminilivedemo/LifeMemoirActivity.kt",
        "app/src/main/res/layout/activity_life_memoir.xml",
        "app/src/main/res/layout/item_memoir.xml"
    ]
    
    missing_files = []
    for file_path in key_files:
        full_path = android_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Android project structure is complete")
    return True

def check_gradle_files():
    """Check Gradle configuration"""
    print("\n🔍 Checking Gradle configuration...")
    
    android_path = Path("GeminiLiveDemo")
    gradle_files = [
        "build.gradle.kts",
        "app/build.gradle.kts",
        "settings.gradle.kts",
        "gradle.properties"
    ]
    
    for gradle_file in gradle_files:
        file_path = android_path / gradle_file
        if file_path.exists():
            print(f"✅ {gradle_file} exists")
        else:
            print(f"❌ {gradle_file} missing")
            return False
    
    return True

def check_manifest():
    """Check AndroidManifest.xml for memoir activities"""
    print("\n🔍 Checking AndroidManifest.xml...")
    
    manifest_path = Path("GeminiLiveDemo/app/src/main/AndroidManifest.xml")
    if not manifest_path.exists():
        print("❌ AndroidManifest.xml not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for memoir activities
        activities = [
            "LifeMemoirActivity",
            "MemoirDetailActivity"
        ]
        
        missing_activities = []
        for activity in activities:
            if activity not in content:
                missing_activities.append(activity)
        
        if missing_activities:
            print(f"❌ Missing activities in manifest: {missing_activities}")
            return False
        
        print("✅ All memoir activities found in manifest")
        return True
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def check_layout_files():
    """Check layout files for memoir UI"""
    print("\n🔍 Checking layout files...")
    
    layout_path = Path("GeminiLiveDemo/app/src/main/res/layout")
    if not layout_path.exists():
        print("❌ Layout directory not found")
        return False
    
    required_layouts = [
        "activity_life_memoir.xml",
        "item_memoir.xml",
        "activity_memoir_detail.xml"
    ]
    
    missing_layouts = []
    for layout in required_layouts:
        layout_file = layout_path / layout
        if not layout_file.exists():
            missing_layouts.append(layout)
    
    if missing_layouts:
        print(f"❌ Missing layout files: {missing_layouts}")
        return False
    
    print("✅ All required layout files found")
    return True

def check_kotlin_files():
    """Check Kotlin source files"""
    print("\n🔍 Checking Kotlin source files...")
    
    kotlin_path = Path("GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo")
    if not kotlin_path.exists():
        print("❌ Kotlin source directory not found")
        return False
    
    required_files = [
        "LifeMemoirActivity.kt",
        "MemoirDetailActivity.kt",
        "adapters/MemoirAdapter.kt",
        "data/ApiClient.kt",
        "data/ApiService.kt"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = kotlin_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing Kotlin files: {missing_files}")
        return False
    
    print("✅ All required Kotlin files found")
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    print("\n🔍 Checking dependencies...")
    
    # Check if Java/Android SDK is available
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Java is available")
        else:
            print("❌ Java not available")
            return False
    except Exception:
        print("❌ Java not available")
        return False
    
    # Check if Gradle is available
    gradle_path = Path("GeminiLiveDemo/gradlew")
    if gradle_path.exists():
        print("✅ Gradle wrapper found")
    else:
        print("❌ Gradle wrapper not found")
        return False
    
    return True

def suggest_build_commands():
    """Suggest build commands for Android app"""
    print("\n🚀 Android App Build Instructions:")
    print("=" * 50)
    
    print("\n1. Navigate to Android project:")
    print("   cd GeminiLiveDemo")
    
    print("\n2. Clean and build project:")
    print("   ./gradlew clean")
    print("   ./gradlew build")
    
    print("\n3. Install on device/emulator:")
    print("   ./gradlew installDebug")
    
    print("\n4. Run app:")
    print("   ./gradlew runDebug")
    
    print("\n5. Generate APK:")
    print("   ./gradlew assembleDebug")
    
    print("\n📱 Testing Memoir Features:")
    print("- Launch app and login")
    print("- Navigate to 'Life Memoir' section")
    print("- Check if memoirs are loaded from API")
    print("- Test search functionality")
    print("- Test memoir detail view")

def main():
    """Main test function"""
    print("🔍 Android App Build Test")
    print("=" * 50)
    
    checks = [
        check_android_project,
        check_gradle_files,
        check_manifest,
        check_layout_files,
        check_kotlin_files,
        check_dependencies
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Android app is ready to build.")
        suggest_build_commands()
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("- Ensure all required files exist")
        print("- Check file paths and permissions")
        print("- Install Java and Android SDK")
        print("- Update Gradle configuration")

if __name__ == "__main__":
    main() 