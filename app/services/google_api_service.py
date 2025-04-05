
"""
خدمة واجهة برمجة تطبيقات Google لنظام تقييم BTEC
توفر واجهة لخدمات Google المختلفة مثل Sheets وDrive وTranslate
"""

import os
import logging
from typing import Optional, Dict, Any, List

import requests
from flask import current_app

# إعداد التسجيل
logger = logging.getLogger(__name__)

class GoogleAPIService:
    """خدمة Google API لنظام تقييم BTEC"""
    
    def __init__(self, api_key: Optional[str] = None, use_context: bool = False):
        """
        تهيئة خدمة Google API
        
        Args:
            api_key: مفتاح API الخاص بـ Google (اختياري، سيتم استخدام المتغير البيئي أو سياق التطبيق)
            use_context: استخدام سياق تطبيق Flask (اختياري، افتراضيًا False)
        """
        # استخدام مفتاح API المقدم أو البحث عنه في سياق التطبيق أو المتغيرات البيئية
        if api_key:
            self.api_key = api_key
        elif use_context:
            self.api_key = current_app.config.get('GOOGLE_API_KEY')
        else:
            self.api_key = os.environ.get('GOOGLE_API_KEY')
        
        if self.api_key:
            logger.info("تم تهيئة GoogleAPIService بمفتاح API صالح")
            self.enabled = True
        else:
            logger.warning("تحذير: لم يتم توفير مفتاح Google API. الخدمة معطلة.")
            self.enabled = False
    
    def translate_text(self, text: str, target_language: str = 'ar', source_language: str = 'en') -> Optional[str]:
        """
        ترجمة نص باستخدام Google Translate API
        
        Args:
            text: النص المراد ترجمته
            target_language: رمز اللغة الهدف (افتراضيًا العربية 'ar')
            source_language: رمز اللغة المصدر (افتراضيًا الإنجليزية 'en')
        
        Returns:
            النص المترجم أو None إذا فشلت الترجمة
        """
        if not self.enabled:
            logger.warning("محاولة استخدام خدمة الترجمة ولكن الخدمة معطلة.")
            return None
        
        url = f"https://translation.googleapis.com/language/translate/v2?key={self.api_key}"
        payload = {
            'q': text,
            'target': target_language,
            'source': source_language
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result['data']['translations'][0]['translatedText']
            return translated_text
            
        except Exception as e:
            logger.error(f"خطأ في ترجمة النص: {str(e)}")
            return None
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        اكتشاف لغة نص باستخدام Google Translate API
        
        Args:
            text: النص المراد اكتشاف لغته
        
        Returns:
            رمز اللغة المكتشفة أو None إذا فشل الاكتشاف
        """
        if not self.enabled:
            logger.warning("محاولة استخدام خدمة اكتشاف اللغة ولكن الخدمة معطلة.")
            return None
        
        url = f"https://translation.googleapis.com/language/translate/v2/detect?key={self.api_key}"
        payload = {
            'q': text
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            detected_language = result['data']['detections'][0][0]['language']
            return detected_language
            
        except Exception as e:
            logger.error(f"خطأ في اكتشاف لغة النص: {str(e)}")
            return None
    
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على تفاصيل مكان باستخدام Google Places API
        
        Args:
            place_id: معرف المكان
        
        Returns:
            قاموس يحتوي على تفاصيل المكان أو None إذا فشلت العملية
        """
        if not self.enabled:
            logger.warning("محاولة استخدام خدمة الأماكن ولكن الخدمة معطلة.")
            return None
        
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={self.api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            result = response.json()
            if result['status'] == 'OK':
                return result['result']
            else:
                logger.error(f"خطأ في الحصول على تفاصيل المكان: {result['status']}")
                return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على تفاصيل المكان: {str(e)}")
            return None
    
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        تحويل عنوان إلى إحداثيات باستخدام Google Geocoding API
        
        Args:
            address: العنوان المراد تحويله
        
        Returns:
            قاموس يحتوي على معلومات الموقع أو None إذا فشلت العملية
        """
        if not self.enabled:
            logger.warning("محاولة استخدام خدمة الترميز الجغرافي ولكن الخدمة معطلة.")
            return None
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            result = response.json()
            if result['status'] == 'OK':
                return result['results'][0]
            else:
                logger.error(f"خطأ في تحويل العنوان إلى إحداثيات: {result['status']}")
                return None
            
        except Exception as e:
            logger.error(f"خطأ في تحويل العنوان إلى إحداثيات: {str(e)}")
            return None
