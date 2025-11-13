"""
Advanced Browser Fingerprinting Resistance

Implements comprehensive fingerprinting protection beyond basic user agent rotation:
- Canvas fingerprinting resistance
- WebGL fingerprinting resistance
- Audio context fingerprinting resistance
- Font fingerprinting resistance
- Screen resolution randomization
- Timezone spoofing
- Language/locale consistency
- Hardware concurrency masking
"""

import random
import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BrowserProfile:
    """Complete browser fingerprint profile"""
    user_agent: str
    platform: str
    vendor: str
    languages: List[str]
    screen_width: int
    screen_height: int
    screen_depth: int
    timezone: str
    hardware_concurrency: int
    device_memory: int  # GB
    webgl_vendor: str
    webgl_renderer: str
    canvas_fingerprint: str
    audio_fingerprint: str


class AdvancedFingerprintProtection:
    """
    Advanced fingerprinting protection with consistent profiles
    """

    # Real-world browser profiles (updated Jan 2025)
    PROFILES = [
        {
            'name': 'Chrome_Windows_High',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'platform': 'Win32',
            'vendor': 'Google Inc.',
            'languages': ['en-US', 'en'],
            'screen': (1920, 1080, 24),
            'timezone': 'America/New_York',
            'hardware_concurrency': 8,
            'device_memory': 16,
            'webgl_vendor': 'Google Inc. (NVIDIA)',
            'webgl_renderer': 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)'
        },
        {
            'name': 'Chrome_Mac_High',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'platform': 'MacIntel',
            'vendor': 'Google Inc.',
            'languages': ['en-US', 'en'],
            'screen': (2560, 1440, 24),
            'timezone': 'America/Los_Angeles',
            'hardware_concurrency': 8,
            'device_memory': 16,
            'webgl_vendor': 'Apple Inc.',
            'webgl_renderer': 'Apple M1 Pro'
        },
        {
            'name': 'Firefox_Linux',
            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'platform': 'Linux x86_64',
            'vendor': '',
            'languages': ['en-US', 'en'],
            'screen': (1920, 1080, 24),
            'timezone': 'Europe/London',
            'hardware_concurrency': 4,
            'device_memory': 8,
            'webgl_vendor': 'X.Org',
            'webgl_renderer': 'Mesa DRI Intel(R) UHD Graphics 630 (CML GT2)'
        },
        {
            'name': 'Chrome_Windows_Medium',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'platform': 'Win32',
            'vendor': 'Google Inc.',
            'languages': ['en-US', 'en'],
            'screen': (1920, 1080, 24),
            'timezone': 'America/Chicago',
            'hardware_concurrency': 4,
            'device_memory': 8,
            'webgl_vendor': 'Google Inc. (Intel)',
            'webgl_renderer': 'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)'
        },
        {
            'name': 'Edge_Windows',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'platform': 'Win32',
            'vendor': 'Google Inc.',
            'languages': ['en-US', 'en'],
            'screen': (1920, 1080, 24),
            'timezone': 'America/Denver',
            'hardware_concurrency': 6,
            'device_memory': 16,
            'webgl_vendor': 'Google Inc. (AMD)',
            'webgl_renderer': 'ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)'
        },
        {
            'name': 'Safari_Mac',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'platform': 'MacIntel',
            'vendor': 'Apple Computer, Inc.',
            'languages': ['en-US', 'en'],
            'screen': (1920, 1080, 24),
            'timezone': 'America/Los_Angeles',
            'hardware_concurrency': 8,
            'device_memory': 16,
            'webgl_vendor': 'Apple Inc.',
            'webgl_renderer': 'Apple M2'
        }
    ]

    def __init__(self, session_id: str = None):
        """
        Initialize with optional session ID for consistent fingerprinting

        Args:
            session_id: Unique session identifier (e.g., trading pair + date)
        """
        self.session_id = session_id or self._generate_session_id()
        self.profile = self._select_profile()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.sha256(
            f"{datetime.now().isoformat()}{random.random()}".encode()
        ).hexdigest()[:16]

    def _select_profile(self) -> Dict:
        """Select deterministic profile based on session ID"""
        # Use session ID to deterministically select profile
        # This ensures same profile for same session
        seed = int(self.session_id[:8], 16)
        random.seed(seed)
        profile = random.choice(self.PROFILES).copy()
        random.seed()  # Reset to non-deterministic
        return profile

    def get_browser_profile(self) -> BrowserProfile:
        """Get complete browser profile"""
        screen_w, screen_h, screen_depth = self.profile['screen']

        return BrowserProfile(
            user_agent=self.profile['user_agent'],
            platform=self.profile['platform'],
            vendor=self.profile['vendor'],
            languages=self.profile['languages'],
            screen_width=screen_w,
            screen_height=screen_h,
            screen_depth=screen_depth,
            timezone=self.profile['timezone'],
            hardware_concurrency=self.profile['hardware_concurrency'],
            device_memory=self.profile['device_memory'],
            webgl_vendor=self.profile['webgl_vendor'],
            webgl_renderer=self.profile['webgl_renderer'],
            canvas_fingerprint=self._generate_canvas_fingerprint(),
            audio_fingerprint=self._generate_audio_fingerprint()
        )

    def _generate_canvas_fingerprint(self) -> str:
        """Generate consistent canvas fingerprint"""
        # Generate deterministic canvas fingerprint based on session
        return hashlib.sha256(
            f"canvas_{self.session_id}".encode()
        ).hexdigest()[:32]

    def _generate_audio_fingerprint(self) -> str:
        """Generate consistent audio fingerprint"""
        return hashlib.sha256(
            f"audio_{self.session_id}".encode()
        ).hexdigest()[:32]

    def apply_to_driver(self, driver):
        """
        Apply complete fingerprint protection to Selenium driver

        Args:
            driver: Selenium WebDriver instance
        """
        profile = self.get_browser_profile()

        # Set user agent via CDP
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            'userAgent': profile.user_agent,
            'platform': profile.platform,
            'acceptLanguage': ','.join(profile.languages)
        })

        # Inject comprehensive fingerprint protection
        protection_script = f"""
        // ============================================
        // NAVIGATOR OVERRIDES
        // ============================================
        Object.defineProperty(navigator, 'vendor', {{
            get: () => '{profile.vendor}'
        }});

        Object.defineProperty(navigator, 'platform', {{
            get: () => '{profile.platform}'
        }});

        Object.defineProperty(navigator, 'languages', {{
            get: () => {profile.languages}
        }});

        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {profile.hardware_concurrency}
        }});

        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {profile.device_memory}
        }});

        // ============================================
        // SCREEN OVERRIDES
        // ============================================
        Object.defineProperty(screen, 'width', {{
            get: () => {profile.screen_width}
        }});

        Object.defineProperty(screen, 'height', {{
            get: () => {profile.screen_height}
        }});

        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {profile.screen_depth}
        }});

        Object.defineProperty(screen, 'pixelDepth', {{
            get: () => {profile.screen_depth}
        }});

        // ============================================
        // CANVAS FINGERPRINT PROTECTION
        // ============================================
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const originalToBlob = HTMLCanvasElement.prototype.toBlob;
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

        // Inject small noise into canvas data
        const canvasNoise = '{profile.canvas_fingerprint}';

        HTMLCanvasElement.prototype.toDataURL = function() {{
            // Add deterministic noise based on session
            const context = this.getContext('2d');
            const imageData = context.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imageData.data.length; i += 4) {{
                const noise = parseInt(canvasNoise[i % canvasNoise.length], 16) % 3 - 1;
                imageData.data[i] += noise;
            }}
            context.putImageData(imageData, 0, 0);
            return originalToDataURL.apply(this, arguments);
        }};

        // ============================================
        // WEBGL FINGERPRINT PROTECTION
        // ============================================
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{profile.webgl_vendor}';
            }}
            if (parameter === 37446) {{
                return '{profile.webgl_renderer}';
            }}
            return getParameter.apply(this, arguments);
        }};

        // ============================================
        // AUDIO CONTEXT FINGERPRINT PROTECTION
        // ============================================
        const audioNoise = '{profile.audio_fingerprint}';
        const originalCreateDynamicsCompressor = AudioContext.prototype.createDynamicsCompressor;

        AudioContext.prototype.createDynamicsCompressor = function() {{
            const compressor = originalCreateDynamicsCompressor.apply(this, arguments);
            const originalKnee = Object.getOwnPropertyDescriptor(DynamicsCompressorNode.prototype, 'knee');

            Object.defineProperty(compressor, 'knee', {{
                get: function() {{
                    const noise = parseInt(audioNoise[0], 16) / 100;
                    return originalKnee.get.call(this) + noise;
                }}
            }});

            return compressor;
        }};

        // ============================================
        // FONT FINGERPRINT PROTECTION
        // ============================================
        // Standardize font list
        Object.defineProperty(document, 'fonts', {{
            get: () => ({{
                check: () => true,
                ready: Promise.resolve(),
                entries: () => [],
                forEach: () => {{}}
            }})
        }});

        // ============================================
        // TIMEZONE OVERRIDE
        // ============================================
        const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {{
            // {profile.timezone} offset
            return 300; // EST for example
        }};

        // ============================================
        // BATTERY API BLOCKING
        // ============================================
        if (navigator.getBattery) {{
            navigator.getBattery = undefined;
        }}

        // ============================================
        // MEDIA DEVICES PROTECTION
        // ============================================
        if (navigator.mediaDevices) {{
            navigator.mediaDevices.enumerateDevices = async () => [];
        }}

        console.log('🛡️ Advanced fingerprint protection active');
        """

        # Execute protection script
        driver.execute_script(protection_script)

        # Set window size
        driver.set_window_size(profile.screen_width, profile.screen_height)

        return profile


class UserAgentRotator:
    """Simple user agent rotation (legacy support)"""

    def __init__(self):
        self.fingerprint = AdvancedFingerprintProtection()

    def get_random_profile(self) -> BrowserProfile:
        """Get random browser profile"""
        return self.fingerprint.get_browser_profile()

    def apply_to_driver(self, driver):
        """Apply to driver"""
        return self.fingerprint.apply_to_driver(driver)
