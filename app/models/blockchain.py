"""
نموذج التحقق من سلسلة الكتل في نظام تقييم BTEC
"""

from datetime import datetime

from app.extensions import db


class BlockchainVerification(db.Model):
    """نموذج التحقق من سلسلة الكتل في نظام تقييم BTEC."""
    __tablename__ = 'blockchain_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'))
    hash_value = db.Column(db.String(256), nullable=False)
    transaction_id = db.Column(db.String(256), nullable=False)
    blockchain_type = db.Column(db.String(50), default='ethereum')
    verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlockchainVerification {self.id} - Evaluation {self.evaluation_id}>'
    
    def verify_on_blockchain(self):
        """التحقق من صحة البيانات على البلوكشين.
        
        يستخدم هذا الأسلوب للتحقق من صحة بيانات التقييم على البلوكشين باستخدام
        معرف المعاملة وقيمة التجزئة المخزنة.
        
        Returns:
            bool: True إذا تم التحقق بنجاح، False خلاف ذلك
        """
        # TODO: تنفيذ التحقق الفعلي باستخدام Web3 أو API خاص بالبلوكشين
        
        # في حالة نجاح التحقق
        self.verified = True
        self.verification_date = datetime.utcnow()
        return True
    
    def generate_verification_url(self):
        """إنشاء URL للتحقق من المعاملة على مستكشف البلوكشين.
        
        Returns:
            str: URL للتحقق من المعاملة
        """
        if self.blockchain_type == 'ethereum':
            # استخدام Etherscan للشبكة الرئيسية
            return f'https://etherscan.io/tx/{self.transaction_id}'
        elif self.blockchain_type == 'ethereum_testnet':
            # استخدام Etherscan لشبكة Ropsten التجريبية
            return f'https://ropsten.etherscan.io/tx/{self.transaction_id}'
        elif self.blockchain_type == 'polygon':
            # استخدام Polygonscan
            return f'https://polygonscan.com/tx/{self.transaction_id}'
        else:
            # في حالة عدم معرفة نوع البلوكشين
            return '#'
    
    def to_dict(self):
        """تحويل بيانات التحقق من البلوكشين إلى قاموس.
        
        Returns:
            dict: بيانات التحقق
        """
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'hash_value': self.hash_value,
            'transaction_id': self.transaction_id,
            'blockchain_type': self.blockchain_type,
            'verified': self.verified,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verification_url': self.generate_verification_url()
        }