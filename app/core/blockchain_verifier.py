"""
وحدة التحقق من البلوكتشين في نظام تقييم BTEC
"""
import json
import logging
import os
import time
from datetime import datetime
from functools import wraps

import requests
from flask import current_app
from web3 import Web3
from web3.exceptions import BlockNotFound, ContractLogicError

logger = logging.getLogger(__name__)

def blockchain_required(f):
    """
    زخرفة للتأكد من وجود اتصال بالبلوكتشين
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        skip_blockchain = current_app.config.get('SKIP_BLOCKCHAIN_VERIFICATION', False)
        if skip_blockchain:
            logger.warning("تم تخطي التحقق من البلوكتشين (وضع التخطي)")
            return f(*args, **kwargs)
        
        verifier = BlockchainVerifier()
        if not verifier.connected:
            logger.error("فشل الاتصال بالبلوكتشين")
            return {
                'success': False,
                'error': 'فشل الاتصال بالبلوكتشين. يرجى التحقق من الإعدادات.'
            }
        
        return f(*args, **kwargs)
    return decorated_function


class BlockchainVerifier:
    """
    فئة للتحقق من البلوكتشين
    """
    
    def __init__(self, infura_url=None, contract_address=None, signer_private_key=None):
        """
        تهيئة المتحقق
        
        Args:
            infura_url: عنوان URL لخدمة Infura
            contract_address: عنوان العقد الذكي
            signer_private_key: المفتاح الخاص للموقّع
        """
        self.infura_url = infura_url or os.environ.get('INFURA_URL') or current_app.config.get('INFURA_URL')
        self.contract_address = contract_address or os.environ.get('CONTRACT_ADDRESS') or current_app.config.get('CONTRACT_ADDRESS')
        self.signer_private_key = signer_private_key or os.environ.get('SIGNER_PRIVATE_KEY') or current_app.config.get('SIGNER_PRIVATE_KEY')
        
        self.web3 = None
        self.contract = None
        self.connected = False
        self.skip_verification = current_app.config.get('SKIP_BLOCKCHAIN_VERIFICATION', False)
        
        # تسجيل ما إذا كان سيتم تخطي التحقق
        if self.skip_verification:
            logger.warning("تشغيل المتحقق في وضع التخطي (وضع المحاكاة)")
        
        # محاولة الاتصال بالبلوكتشين
        self._connect()
    
    def _connect(self):
        """
        الاتصال بالبلوكتشين
        
        Returns:
            bool: ما إذا تم الاتصال بنجاح
        """
        if self.skip_verification:
            self.connected = True
            return True
        
        if not self.infura_url:
            logger.warning("لم يتم توفير عنوان URL لخدمة Infura")
            return False
        
        try:
            # الاتصال بشبكة إثيريوم
            self.web3 = Web3(Web3.HTTPProvider(self.infura_url))
            
            # التحقق من الاتصال
            if not self.web3.is_connected():
                logger.error("فشل الاتصال بشبكة إثيريوم")
                return False
            
            logger.info(f"تم الاتصال بنجاح بشبكة إثيريوم (آخر كتلة: {self.web3.eth.block_number})")
            
            # تحميل العقد إذا تم توفير عنوانه
            if self.contract_address:
                # تحميل ABI
                contract_abi = self._load_contract_abi()
                if contract_abi:
                    self.contract = self.web3.eth.contract(
                        address=self.contract_address,
                        abi=contract_abi
                    )
                    logger.info(f"تم تحميل العقد بنجاح: {self.contract_address}")
                else:
                    logger.warning("لم يتم توفير ABI للعقد")
            
            self.connected = True
            return True
        
        except Exception as e:
            logger.error(f"خطأ أثناء الاتصال بالبلوكتشين: {str(e)}")
            self.web3 = None
            self.contract = None
            self.connected = False
            return False
    
    def _load_contract_abi(self):
        """
        تحميل ABI للعقد
        
        Returns:
            list: ABI للعقد
        """
        try:
            # يمكن استخراج ABI من ملف
            contract_abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'blockchain', 'contract_abi.json')
            
            if os.path.exists(contract_abi_path):
                with open(contract_abi_path, 'r') as f:
                    return json.load(f)
            
            # أو يمكن استخدام ABI المخزن في التكوين
            contract_abi = current_app.config.get('CONTRACT_ABI')
            if contract_abi:
                if isinstance(contract_abi, str):
                    return json.loads(contract_abi)
                return contract_abi
            
            logger.warning("لم يتم العثور على ABI للعقد")
            
            # ABI أساسي للإستخدام
            return [
                {
                    "constant": True,
                    "inputs": [{"name": "hash", "type": "string"}],
                    "name": "verifyHash",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                },
                {
                    "constant": False,
                    "inputs": [{"name": "hash", "type": "string"}, {"name": "data", "type": "string"}],
                    "name": "storeHash",
                    "outputs": [],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [{"name": "hash", "type": "string"}],
                    "name": "getHashData",
                    "outputs": [{"name": "", "type": "string"}, {"name": "", "type": "uint256"}],
                    "type": "function"
                }
            ]
        
        except Exception as e:
            logger.error(f"خطأ أثناء تحميل ABI للعقد: {str(e)}")
            return None
    
    def verify_hash(self, hash_str):
        """
        التحقق من وجود الهاش في البلوكتشين
        
        Args:
            hash_str: الهاش المراد التحقق منه
            
        Returns:
            dict: نتيجة التحقق
        """
        if self.skip_verification:
            # محاكاة التحقق في وضع التخطي
            timestamp = int(time.time())
            return {
                'success': True,
                'verified': True,
                'timestamp': timestamp,
                'block_number': 0,
                'hash': hash_str,
                'verification_time': datetime.fromtimestamp(timestamp).isoformat(),
                'note': 'تم التحقق في وضع المحاكاة (تم تخطي التحقق الفعلي من البلوكتشين)'
            }
        
        if not self.connected or not self.contract:
            return {
                'success': False,
                'error': 'لم يتم توصيل المتحقق بالبلوكتشين',
                'verified': False
            }
        
        try:
            # استدعاء وظيفة التحقق في العقد
            result = self.contract.functions.verifyHash(hash_str).call()
            
            if result:
                # الحصول على بيانات الهاش المخزنة
                hash_data, timestamp = self.contract.functions.getHashData(hash_str).call()
                
                return {
                    'success': True,
                    'verified': True,
                    'timestamp': timestamp,
                    'block_number': self.web3.eth.block_number,
                    'hash': hash_str,
                    'hash_data': hash_data,
                    'verification_time': datetime.fromtimestamp(timestamp).isoformat()
                }
            else:
                return {
                    'success': True,
                    'verified': False,
                    'hash': hash_str,
                    'verification_time': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"خطأ أثناء التحقق من الهاش: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'verified': False,
                'hash': hash_str
            }
    
    def store_hash(self, hash_str, data_str=None):
        """
        تخزين الهاش في البلوكتشين
        
        Args:
            hash_str: الهاش المراد تخزينه
            data_str: البيانات المرتبطة بالهاش
            
        Returns:
            dict: نتيجة العملية
        """
        if self.skip_verification:
            # محاكاة التخزين في وضع التخطي
            timestamp = int(time.time())
            return {
                'success': True,
                'hash': hash_str,
                'timestamp': timestamp,
                'storage_time': datetime.fromtimestamp(timestamp).isoformat(),
                'note': 'تم التخزين في وضع المحاكاة (تم تخطي التخزين الفعلي في البلوكتشين)'
            }
        
        if not self.connected or not self.contract:
            return {
                'success': False,
                'error': 'لم يتم توصيل المتحقق بالبلوكتشين'
            }
        
        if not self.signer_private_key:
            return {
                'success': False,
                'error': 'لم يتم توفير المفتاح الخاص للموقّع'
            }
        
        try:
            # إعداد الحساب
            account = self.web3.eth.account.from_key(self.signer_private_key)
            
            # البيانات المرتبطة بالهاش
            if data_str is None:
                data_str = f"{hash_str}_data_{int(time.time())}"
            
            # تحضير المعاملة
            nonce = self.web3.eth.get_transaction_count(account.address)
            
            # بناء المعاملة
            tx = self.contract.functions.storeHash(hash_str, data_str).build_transaction({
                'from': account.address,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce
            })
            
            # توقيع المعاملة
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.signer_private_key)
            
            # إرسال المعاملة
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # انتظار تأكيد المعاملة
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if tx_receipt.status == 1:
                return {
                    'success': True,
                    'transaction_hash': tx_receipt.transactionHash.hex(),
                    'block_number': tx_receipt.blockNumber,
                    'block_hash': tx_receipt.blockHash.hex(),
                    'hash': hash_str,
                    'storage_time': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'فشلت المعاملة',
                    'transaction_hash': tx_receipt.transactionHash.hex()
                }
        
        except Exception as e:
            logger.error(f"خطأ أثناء تخزين الهاش: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_hash(self, data):
        """
        توليد هاش من البيانات
        
        Args:
            data: البيانات المراد توليد هاش لها
            
        Returns:
            str: الهاش المولد
        """
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data, sort_keys=True)
        
        if not isinstance(data, str):
            data = str(data)
        
        # استخدام keccak256 لتوليد الهاش (وهو نفس الهاش المستخدم في إثيريوم)
        if self.web3:
            return self.web3.keccak(text=data).hex()
        else:
            # استخدام hashlib في حالة عدم وجود web3
            import hashlib
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def verify_evaluation(self, evaluation):
        """
        التحقق من صحة تقييم
        
        Args:
            evaluation: بيانات التقييم
            
        Returns:
            dict: نتيجة التحقق
        """
        # توليد هاش للتقييم
        evaluation_data = {
            'id': evaluation.get('id'),
            'uuid': evaluation.get('uuid'),
            'title': evaluation.get('title'),
            'submission_text': evaluation.get('submission_text'),
            'grade': evaluation.get('grade'),
            'evaluator_id': evaluation.get('evaluator_id'),
            'student_id': evaluation.get('student_id'),
            'created_at': evaluation.get('created_at')
        }
        
        hash_str = self.generate_hash(evaluation_data)
        
        # التحقق من الهاش
        verification_result = self.verify_hash(hash_str)
        
        if verification_result.get('verified', False):
            return {
                'success': True,
                'verified': True,
                'hash': hash_str,
                'timestamp': verification_result.get('timestamp'),
                'verification_time': verification_result.get('verification_time'),
                'evaluation_id': evaluation.get('id'),
                'evaluation_uuid': evaluation.get('uuid')
            }
        else:
            return {
                'success': verification_result.get('success', False),
                'verified': False,
                'hash': hash_str,
                'error': verification_result.get('error'),
                'evaluation_id': evaluation.get('id'),
                'evaluation_uuid': evaluation.get('uuid')
            }
    
    def store_evaluation(self, evaluation):
        """
        تخزين تقييم في البلوكتشين
        
        Args:
            evaluation: بيانات التقييم
            
        Returns:
            dict: نتيجة التخزين
        """
        # توليد هاش للتقييم
        evaluation_data = {
            'id': evaluation.get('id'),
            'uuid': evaluation.get('uuid'),
            'title': evaluation.get('title'),
            'submission_text': evaluation.get('submission_text'),
            'grade': evaluation.get('grade'),
            'evaluator_id': evaluation.get('evaluator_id'),
            'student_id': evaluation.get('student_id'),
            'created_at': evaluation.get('created_at')
        }
        
        # تعيين التوقيت بشكل صريح إذا لم يكن موجودًا
        if 'created_at' not in evaluation_data or not evaluation_data['created_at']:
            evaluation_data['created_at'] = datetime.utcnow().isoformat()
        
        hash_str = self.generate_hash(evaluation_data)
        
        # تخزين بيانات التقييم كنص JSON
        data_str = json.dumps({
            'evaluation_id': evaluation.get('id'),
            'evaluation_uuid': evaluation.get('uuid'),
            'grade': evaluation.get('grade'),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # تخزين الهاش
        storage_result = self.store_hash(hash_str, data_str)
        
        if storage_result.get('success', False):
            return {
                'success': True,
                'hash': hash_str,
                'transaction_hash': storage_result.get('transaction_hash'),
                'block_number': storage_result.get('block_number'),
                'storage_time': storage_result.get('storage_time'),
                'evaluation_id': evaluation.get('id'),
                'evaluation_uuid': evaluation.get('uuid')
            }
        else:
            return {
                'success': False,
                'hash': hash_str,
                'error': storage_result.get('error'),
                'evaluation_id': evaluation.get('id'),
                'evaluation_uuid': evaluation.get('uuid')
            }