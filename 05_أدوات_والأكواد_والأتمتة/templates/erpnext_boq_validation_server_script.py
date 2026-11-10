# ==============================================================================
# سكربت الخادم لحماية موازنة بنود المشروع وجدول الكميات (BOQ) في ERPNext
# اسم الموديول: Frappe / ERPNext Server Script
# نوع السكربت: DocType Event
# المستند المطبق عليه: Purchase Invoice / Subcontractor Claim
# الحدث: Before Submit (docstatus == 1)
# حقوق الاستخدام: قناة الذكاء المؤسسي © 2026
# ==============================================================================

import frappe
from frappe import _

def execute(doc, method=None):
    """
    يقوم هذا السكربت بالتحقق من عدم تجاوز كمية البند المفوترة لإجمالي الكمية
    المعتمدة في جدول الكميات (BOQ) للمشروع، ويمنع اعتماد المستخلص إذا حدث تجاوز.
    """
    if not doc.project:
        # إذا لم يكن المستخلص مرتبطاً بمشروع يتم التخطي أو فرض ربطه
        return

    # التحقق من كل بند داخل جدول البنود
    for item in doc.items:
        if not item.item_code:
            continue

        # 1. جلب الحد الأقصى للكمية المعتمدة للبند في موازنة المشروع
        boq_data = frappe.db.sql("""
            SELECT allocated_qty, custom_boq_budget_amount 
            FROM `tabProject BOQ Item`
            WHERE parent = %s AND item_code = %s
        """, (doc.project, item.item_code), as_dict=True)

        if not boq_data:
            # في حال لم يكن البند مسجلاً في الـ BOQ يتم تنبيه الإدارة
            frappe.throw(
                _("خطأ حوكمة: البند {0} غير مدرج في جدول الكميات المعتمد (BOQ) للمشروع {1}!")
                .format(frappe.bold(item.item_code), frappe.bold(doc.project))
            )

        max_allowed_qty = boq_data[0].allocated_qty or 0.0

        # 2. حساب إجمالي الكميات المعتمدة سابقاً في فواتير ومستخلصات مؤكدة
        previous_billed_qty = frappe.db.sql("""
            SELECT SUM(pi_item.qty)
            FROM `tabPurchase Invoice Item` pi_item
            INNER JOIN `tabPurchase Invoice` pi ON pi.name = pi_item.parent
            WHERE pi.project = %s 
              AND pi_item.item_code = %s 
              AND pi.docstatus = 1 
              AND pi.name != %s
        """, (doc.project, item.item_code, doc.name))[0][0] or 0.0

        current_total_qty = previous_billed_qty + item.qty

        # 3. المقارنة واتخاذ القرار الصارم
        if current_total_qty > max_allowed_qty:
            exceeded_qty = current_total_qty - max_allowed_qty
            message = _(
                """
                🚨 <b>تحذير رقابي حاسم لمنع النزيف المالي:</b><br><br>
                لا يمكن اعتماد المستخلص للبند: <b>{0}</b>.<br>
                - الكمية المعتمدة في الـ BOQ: <b>{1}</b><br>
                - المنفذ والمفوتر سابقاً: <b>{2}</b><br>
                - المطلوب في هذا المستخلص: <b>{3}</b><br>
                - <span style='color:red;'>مقدار التجاوز غير القانوني: <b>{4}</b></span><br><br>
                ⚠️ <b>الإجراء المطلوب:</b> يجب إصدار وتعميد <u>أمر تغيير (Change Order)</u> رسمي وملحق عقد مالي قبل الصرف!
                """
            ).format(item.item_code, max_allowed_qty, previous_billed_qty, item.qty, exceeded_qty)
            
            frappe.throw(message, title=_("تجاوز موازنة المشروع (Budget Breach)"))

