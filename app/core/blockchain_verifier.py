"""
وحدة التحقق من التقييمات باستخدام تقنية البلوكتشين
"""
import os
import json
import logging
import hashlib
import time
from app.database import log_audit

class BlockchainVerifier:
    """
    فئة للتحقق من صحة التقييمات باستخدام تقنية البلوكتشين
    """
    def __init__(self):
        self.infura_url = os.environ.get('INFURA_URL')
        self.contract_address = os.environ.get('CONTRACT_ADDRESS')
        self.private_key = os.environ.get('SIGNER_PRIVATE_KEY')
        
        # التحقق من وجود بيانات الاتصال بالبلوكتشين
        if not (self.infura_url and self.contract_address and self.private_key):
            logging.warning("لم يتم العثور على بيانات الاتصال بالبلوكتشين. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
        
        # التحقق من تجاوز التحقق من البلوكتشين في بيئة التطوير
        if os.environ.get('SKIP_BLOCKCHAIN_VERIFICATION') == 'True':
            logging.info("تم تجاوز التحقق من البلوكتشين (وضع التطوير)")
            self.simulation_mode = True
    
    def verify_evaluation(self, evaluation):
        """
        التحقق من صحة تقييم وتسجيله على البلوكتشين
        
        Args:
            evaluation: كائن التقييم المراد التحقق منه
            
        Returns:
            dict: نتيجة التحقق
        """
        try:
            if self.simulation_mode:
                # وضع المحاكاة
                return self._mock_verification(evaluation)
            
            # إنشاء هاش للتقييم
            evaluation_hash = self._create_evaluation_hash(evaluation)
            
            # تسجيل التقييم على البلوكتشين
            from web3 import Web3
            from eth_account import Account
            
            # اتصال بشبكة إيثريوم
            web3 = Web3(Web3.HTTPProvider(self.infura_url))
            
            # التحقق من الاتصال
            if not web3.is_connected():
                logging.error("فشل الاتصال بشبكة إيثريوم")
                return {
                    "success": False,
                    "message": "فشل الاتصال بشبكة إيثريوم",
                    "hash": evaluation_hash,
                    "blockchain_tx": None
                }
            
            # تحميل العقد الذكي ABI
            contract_abi = self._get_contract_abi()
            contract = web3.eth.contract(address=self.contract_address, abi=contract_abi)
            
            # إعداد المعاملة
            account = Account.from_key(self.private_key)
            nonce = web3.eth.get_transaction_count(account.address)
            
            # بناء المعاملة لاستدعاء وظيفة recordGrade في العقد
            tx = contract.functions.recordGrade(
                evaluation.id,
                evaluation_hash,
                evaluation.user_id,
                evaluation.grade
            ).build_transaction({
                'from': account.address,
                'gas': 2000000,
                'gasPrice': web3.to_wei('50', 'gwei'),
                'nonce': nonce
            })
            
            # توقيع وإرسال المعاملة
            signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # انتظار تأكيد المعاملة
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # تحديث معلومات التحقق للتقييم
            transaction_hash = receipt.transactionHash.hex()
            
            # تسجيل الحدث في سجل التدقيق
            log_audit("blockchain_verification", f"Evaluation ID: {evaluation.id}", {
                "evaluation_id": evaluation.id,
                "hash": evaluation_hash,
                "transaction_hash": transaction_hash,
                "block_number": receipt.blockNumber
            })
            
            # إرجاع نتيجة ناجحة
            return {
                "success": True,
                "message": "تم التحقق من التقييم وتسجيله على البلوكتشين بنجاح",
                "hash": evaluation_hash,
                "blockchain_tx": transaction_hash,
                "block_number": receipt.blockNumber
            }
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من التقييم على البلوكتشين: {str(e)}")
            
            # تسجيل الخطأ في سجل التدقيق
            log_audit("blockchain_verification_error", f"Evaluation ID: {evaluation.id}", str(e))
            
            # في حالة الفشل، قم بمحاكاة التحقق في وضع التطوير
            if os.environ.get('FLASK_ENV') == 'development':
                return self._mock_verification(evaluation)
            
            # إرجاع نتيجة الفشل
            return {
                "success": False,
                "message": f"فشل التحقق من التقييم: {str(e)}",
                "hash": self._create_evaluation_hash(evaluation),
                "blockchain_tx": None
            }
    
    def _mock_verification(self, evaluation):
        """
        محاكاة للتحقق من صحة التقييم (للتطوير أو عند عدم توفر مفاتيح البلوكتشين)
        """
        # إنشاء هاش للتقييم
        evaluation_hash = self._create_evaluation_hash(evaluation)
        
        # إنشاء هاش معاملة وهمي
        mock_tx_hash = f"0x{hashlib.sha256(f'{evaluation.id}_{time.time()}'.encode()).hexdigest()}"
        
        # تسجيل الحدث في سجل التدقيق
        log_audit("mock_blockchain_verification", f"Evaluation ID: {evaluation.id}", {
            "evaluation_id": evaluation.id,
            "hash": evaluation_hash,
            "transaction_hash": mock_tx_hash,
            "mock": True
        })
        
        # إرجاع نتيجة ناجحة (محاكاة)
        return {
            "success": True,
            "message": "تم التحقق من التقييم وتسجيله على بلوكتشين وهمي (وضع المحاكاة)",
            "hash": evaluation_hash,
            "blockchain_tx": mock_tx_hash,
            "mock": True
        }
    
    def _create_evaluation_hash(self, evaluation):
        """
        إنشاء هاش للتقييم
        """
        # إنشاء سلسلة تمثل بيانات التقييم
        evaluation_data = {
            "id": evaluation.id,
            "user_id": evaluation.user_id,
            "content": evaluation.content,
            "grade": evaluation.grade,
            "result": json.dumps(evaluation.result) if evaluation.result else "",
            "created_at": str(evaluation.created_at)
        }
        
        # تحويل البيانات إلى سلسلة JSON وإنشاء هاش SHA-256
        data_string = json.dumps(evaluation_data, sort_keys=True)
        hash_object = hashlib.sha256(data_string.encode())
        
        return hash_object.hexdigest()
    
    def _get_contract_abi(self):
        """
        الحصول على ABI للعقد الذكي
        """
        # في بيئة الإنتاج، يجب تحميل ABI من ملف أو خدمة
        # هنا، نستخدم ABI مبسط للتوضيح
        return [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "evaluationId", "type": "uint256"},
                    {"internalType": "string", "name": "evaluationHash", "type": "string"},
                    {"internalType": "uint256", "name": "userId", "type": "uint256"},
                    {"internalType": "string", "name": "grade", "type": "string"}
                ],
                "name": "recordGrade",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "evaluationId", "type": "uint256"}],
                "name": "verifyGrade",
                "outputs": [
                    {"internalType": "bool", "name": "", "type": "bool"},
                    {"internalType": "string", "name": "", "type": "string"},
                    {"internalType": "uint256", "name": "", "type": "uint256"},
                    {"internalType": "string", "name": "", "type": "string"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
