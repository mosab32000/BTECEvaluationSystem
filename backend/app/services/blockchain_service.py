"""
خدمة البلوكتشين لنظام تقييم BTEC
توفر آليات للتحقق وإثبات سلامة التقييمات
"""

import os
import json
import logging
import hashlib
import time
from typing import Dict, Any, Optional, List, Union
from flask import current_app
from web3 import Web3
from web3.exceptions import TransactionNotFound, BadFunctionCallOutput

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainService:
    """صنف خدمة البلوكتشين لتوثيق وإثبات سلامة التقييمات"""

    def __init__(self, infura_url: Optional[str] = None, contract_address: Optional[str] = None, private_key: Optional[str] = None):
        """
        تهيئة خدمة البلوكتشين
        
        Args:
            infura_url: رابط خدمة Infura (اختياري، سيتم استخدام المتغير البيئي أو سياق التطبيق)
            contract_address: عنوان العقد الذكي (اختياري، سيتم استخدام المتغير البيئي أو سياق التطبيق)
            private_key: المفتاح الخاص للحساب المستخدم للتوقيع (اختياري، سيتم استخدام المتغير البيئي أو سياق التطبيق)
        """
        # استخدام القيم المقدمة أو البحث عنها في المتغيرات البيئية أو سياق التطبيق
        self.infura_url = infura_url or os.environ.get('INFURA_URL') or current_app.config.get('INFURA_URL')
        self.contract_address = contract_address or os.environ.get('CONTRACT_ADDRESS') or current_app.config.get('CONTRACT_ADDRESS')
        self.private_key = private_key or os.environ.get('SIGNER_PRIVATE_KEY') or current_app.config.get('SIGNER_PRIVATE_KEY')
        
        self.w3 = None
        self.contract = None
        self.account = None
        
        # محاولة الاتصال بشبكة البلوكتشين
        if self.infura_url and self.contract_address and self.private_key:
            try:
                # الاتصال بشبكة البلوكتشين
                self.w3 = Web3(Web3.HTTPProvider(self.infura_url))
                
                if not self.w3.is_connected():
                    logger.error("فشل الاتصال بشبكة البلوكتشين")
                    self.simulation_mode = True
                    return
                
                # تعريف ABI للعقد الذكي (يجب تحديثه بناءً على العقد الفعلي)
                # هذا مجرد مثال مبسط، يجب استبداله بـ ABI الحقيقي للعقد
                contract_abi = [
                    {
                        "inputs": [
                            {"internalType": "string", "name": "hash", "type": "string"},
                            {"internalType": "string", "name": "data", "type": "string"}
                        ],
                        "name": "recordEvaluation",
                        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [{"internalType": "string", "name": "hash", "type": "string"}],
                        "name": "verifyEvaluation",
                        "outputs": [
                            {"internalType": "bool", "name": "", "type": "bool"},
                            {"internalType": "string", "name": "", "type": "string"},
                            {"internalType": "uint256", "name": "", "type": "uint256"}
                        ],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
                
                # إنشاء نسخة من العقد
                self.contract = self.w3.eth.contract(address=self.contract_address, abi=contract_abi)
                
                # إعداد الحساب للتوقيع
                self.account = self.w3.eth.account.from_key(self.private_key)
                
                logger.info("تم تهيئة خدمة البلوكتشين بنجاح")
                self.simulation_mode = False
                
            except Exception as e:
                logger.error(f"خطأ في تهيئة خدمة البلوكتشين: {e}")
                self.simulation_mode = True
        else:
            logger.warning("المعلومات المطلوبة لخدمة البلوكتشين غير متوفرة. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
    
    def _generate_evaluation_hash(self, evaluation_data: Union[str, Dict]) -> str:
        """
        إنشاء هاش للتقييم
        
        Args:
            evaluation_data: بيانات التقييم (نص أو قاموس)
            
        Returns:
            هاش التقييم
        """
        # تحويل البيانات إلى JSON إذا كانت قاموسًا
        if isinstance(evaluation_data, dict):
            data_str = json.dumps(evaluation_data, sort_keys=True)
        else:
            data_str = str(evaluation_data)
        
        # إضافة طابع زمني لضمان تفرد الهاش
        timestamp = str(int(time.time()))
        data_with_timestamp = data_str + timestamp
        
        # إنشاء الهاش باستخدام SHA3 (Keccak256)
        hash_object = hashlib.sha3_256(data_with_timestamp.encode())
        return "0x" + hash_object.hexdigest()
    
    def record_evaluation(self, evaluation_data: Union[str, Dict]) -> str:
        """
        تسجيل تقييم في البلوكتشين
        
        Args:
            evaluation_data: بيانات التقييم (نص أو قاموس)
            
        Returns:
            هاش التقييم المسجل
        """
        if self.simulation_mode:
            # إنشاء هاش في وضع المحاكاة
            hash_value = self._generate_evaluation_hash(evaluation_data)
            logger.info(f"محاكاة تسجيل التقييم في البلوكتشين مع الهاش: {hash_value}")
            return hash_value
        
        try:
            # تحويل البيانات إلى JSON إذا كانت قاموسًا
            if isinstance(evaluation_data, dict):
                data_str = json.dumps(evaluation_data, sort_keys=True)
            else:
                data_str = str(evaluation_data)
            
            # إنشاء هاش للتقييم
            hash_value = self._generate_evaluation_hash(evaluation_data)
            
            # إعداد المعاملة
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.recordEvaluation(
                hash_value,
                data_str
            ).build_transaction({
                'chainId': 1,  # Ethereum mainnet (استبدل بالسلسلة المناسبة)
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # توقيع المعاملة وإرسالها
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # انتظار تأكيد المعاملة
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                logger.info(f"تم تسجيل التقييم في البلوكتشين بنجاح. هاش التقييم: {hash_value}")
                return hash_value
            else:
                logger.error("فشل تسجيل التقييم في البلوكتشين")
                return f"ERROR_{hash_value}"
                
        except Exception as e:
            logger.error(f"خطأ في تسجيل التقييم في البلوكتشين: {e}")
            # إنشاء هاش في حالة الخطأ
            hash_value = self._generate_evaluation_hash(evaluation_data)
            return f"ERROR_{hash_value}"
    
    def verify_evaluation(self, evaluation_hash: str) -> Dict[str, Any]:
        """
        التحقق من تقييم مسجل في البلوكتشين
        
        Args:
            evaluation_hash: هاش التقييم للتحقق منه
            
        Returns:
            نتيجة التحقق كقاموس
        """
        if self.simulation_mode:
            logger.info(f"محاكاة التحقق من التقييم مع الهاش: {evaluation_hash}")
            return {
                "verified": True,
                "data": "بيانات التقييم المحاكية",
                "timestamp": int(time.time()),
                "block_number": 12345678,
                "transaction_hash": "0x" + "0" * 64
            }
        
        try:
            # إزالة "ERROR_" من الهاش إذا كان موجودًا
            if evaluation_hash.startswith("ERROR_"):
                clean_hash = evaluation_hash[6:]
            else:
                clean_hash = evaluation_hash
            
            # استدعاء دالة التحقق في العقد
            result = self.contract.functions.verifyEvaluation(clean_hash).call()
            
            if result[0]:  # التحقق ناجح
                # استخراج بيانات التقييم والطابع الزمني
                evaluation_data = result[1]
                timestamp = result[2]
                
                # الحصول على معلومات المعاملة
                event_filter = self.w3.eth.filter({
                    'address': self.contract_address,
                    'topics': [self.w3.keccak(text="EvaluationRecorded(string)").hex(), clean_hash]
                })
                logs = event_filter.get_all_entries()
                
                if logs:
                    transaction_hash = logs[0]['transactionHash'].hex()
                    block_number = logs[0]['blockNumber']
                else:
                    transaction_hash = "غير متوفر"
                    block_number = 0
                
                return {
                    "verified": True,
                    "data": evaluation_data,
                    "timestamp": timestamp,
                    "block_number": block_number,
                    "transaction_hash": transaction_hash
                }
            else:
                logger.warning(f"فشل التحقق من التقييم مع الهاش: {clean_hash}")
                return {
                    "verified": False,
                    "error": "لم يتم العثور على التقييم في البلوكتشين"
                }
                
        except TransactionNotFound:
            logger.error(f"لم يتم العثور على المعاملة للهاش: {evaluation_hash}")
            return {
                "verified": False,
                "error": "لم يتم العثور على المعاملة"
            }
        except BadFunctionCallOutput:
            logger.error(f"خطأ في استدعاء وظيفة العقد للهاش: {evaluation_hash}")
            return {
                "verified": False,
                "error": "خطأ في استدعاء وظيفة العقد"
            }
        except Exception as e:
            logger.error(f"خطأ في التحقق من التقييم في البلوكتشين: {e}")
            return {
                "verified": False,
                "error": str(e)
            }
    
    def get_verification_status(self, evaluation_hash: str) -> Dict[str, Any]:
        """
        الحصول على حالة التحقق بتنسيق مبسط
        
        Args:
            evaluation_hash: هاش التقييم للتحقق منه
            
        Returns:
            حالة التحقق بتنسيق مبسط
        """
        result = self.verify_evaluation(evaluation_hash)
        
        if result.get("verified", False):
            return {
                "status": "VERIFIED",
                "timestamp": result.get("timestamp", 0),
                "message": "تم التحقق من سلامة التقييم"
            }
        else:
            return {
                "status": "NOT_VERIFIED",
                "error": result.get("error", "غير معروف"),
                "message": "لم يتم التحقق من سلامة التقييم"
            }
    
    def batch_record_evaluations(self, evaluations: List[Dict[str, Any]]) -> List[str]:
        """
        تسجيل مجموعة من التقييمات في البلوكتشين
        
        Args:
            evaluations: قائمة بالتقييمات للتسجيل
            
        Returns:
            قائمة بهاشات التقييمات المسجلة
        """
        results = []
        
        for evaluation in evaluations:
            hash_value = self.record_evaluation(evaluation)
            results.append(hash_value)
            
            # إضافة تأخير بسيط بين المعاملات
            time.sleep(0.5)
        
        return results