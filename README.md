Some time ago Apple added JSON build output to `xcodebuild` in the form of the `-resultStreamPath` parameter.
Unfortunately, one can't just `-resultStreamPath -` to replace the STDOUT with a nice stream of JSON fragments so I've created this little wrapper to capture the file stream and show a summary.

Run `./xcodebuild.py -scheme HelloWorld` to get the following output:

<pre>
<b>System</b> rm -rf build
<b>System</b> mkdir -p build
<b>System</b> touch build/ResultStream.json
<b>System</b> touch build/StandardOut.txt
<b>System</b> touch build/StandardError.txt
<b>System</b> xcodebuild -scheme HelloWorld -resultBundlePath build/Result.xcresult -resultStreamPath build/ResultStream.json -derivedDataPath build -resultBundleVersion 3
<b>Building</b> project HelloWorld with scheme HelloWorld
<b>CreateBuildDirectory</b> .../XcodeJsonBuild/build/Build/Products
<b>CreateBuildDirectory</b> .../XcodeJsonBuild/build/Build/Intermediates.noindex
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/DerivedSources/Entitlements.plist
<b>Process</b> product packaging
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/all-product-headers.yaml
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/HelloWorld-project-headers.hmap
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/HelloWorld.hmap
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/HelloWorld-all-non-framework-target-headers.hmap
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/HelloWorld-generated-files.hmap
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/HelloWorld-own-target-headers.hmap
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/HelloWorld-all-target-headers.hmap
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/Script-0694AC5625D97995007E9D22.sh
<b>Script</b> Important setup
<b>Write</b> .../HelloWorld.build/Debug/HelloWorld.build/Objects-normal/x86_64/HelloWorld.LinkFileList
<b>Compile</b> .../XcodeJsonBuild/HelloWorld/main.m
<b>Link</b> .../XcodeJsonBuild/build/Build/Products/Debug/HelloWorld
<b>Sign</b> .../XcodeJsonBuild/build/Build/Products/Debug/HelloWorld
<b>Register</b> execution policy exception for .../XcodeJsonBuild/build/Build/Products/Debug/HelloWorld
</pre>
