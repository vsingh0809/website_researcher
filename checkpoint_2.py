import inspect
from app.interfaces import SearchProvider, WebCrawler, AIProvider, PDFGenerator

def test_protocols():
    print("Executing Checkpoint 2: Validating Interface Protocols...\n")
    
    protocols = [SearchProvider, WebCrawler, AIProvider, PDFGenerator]
    
    for proto in protocols:
        methods = [func for func in dir(proto) if callable(getattr(proto, func)) and not func.startswith("__")]
        print(f"✅ {proto.__name__} loaded successfully with methods: {', '.join(methods)}")
        
        # Verify async signatures
        for method_name in methods:
            method = getattr(proto, method_name)
            if not inspect.iscoroutinefunction(method):
                print(f"❌ ERROR: {proto.__name__}.{method_name} is not an async def!")
                return
    
    print("\n🎉 CHECKPOINT 2 PASSED: All interfaces are strictly defined and asynchronous.")

if __name__ == "__main__":
    test_protocols()