#!/usr/bin/env python3
# check_specific_appointments.py
"""
🔍 فحص تفصيلي للمواعيد المشبوهة
"""

import sqlite3
from datetime import datetime

def analyze_appointments():
    """تحليل مفصل للمواعيد"""
    print("="*70)
    print("🔍 تحليل مفصل للمواعيد")
    print("="*70)
    
    db_path = "agent_data.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # الحصول على مواعيد اليوم للمستخدم
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                id,
                title,
                description,
                date_time,
                created_at,
                user_id
            FROM appointments
            WHERE date(date_time) = ?
            ORDER BY date_time, created_at
        ''', (today,))
        
        appointments = cursor.fetchall()
        
        if not appointments:
            print("\n⚠️ لا توجد مواعيد لليوم")
            conn.close()
            return
        
        print(f"\n📋 وجدت {len(appointments)} موعد لليوم:\n")
        
        # تجميع حسب الوقت
        by_time = {}
        for apt in appointments:
            apt_id, title, desc, date_time, created_at, user_id = apt
            time = date_time.split(' ')[1][:5]  # HH:MM
            
            if time not in by_time:
                by_time[time] = []
            
            by_time[time].append({
                'id': apt_id,
                'title': title,
                'description': desc,
                'date_time': date_time,
                'created_at': created_at,
                'user_id': user_id
            })
        
        # عرض تفصيلي
        duplicates_found = False
        
        for time, apts in sorted(by_time.items()):
            print(f"⏰ **الساعة {time}** ({len(apts)} موعد):")
            print("-" * 70)
            
            for i, apt in enumerate(apts, 1):
                print(f"\n   [{i}] ID: {apt['id']}")
                print(f"       العنوان: '{apt['title']}'")
                if apt['description']:
                    print(f"       الوصف: '{apt['description']}'")
                print(f"       التاريخ الكامل: {apt['date_time']}")
                print(f"       تم الإنشاء: {apt['created_at']}")
            
            # فحص التشابه
            if len(apts) > 1:
                duplicates_found = True
                print(f"\n   ⚠️ تنبيه: {len(apts)} موعد في نفس الوقت!")
                
                # فحص إذا كانت مكررة
                titles = [a['title'] for a in apts]
                if len(set(titles)) < len(titles):
                    print("   🔴 يبدو أن بعضها مكرر (نفس العنوان)")
                else:
                    print("   🟡 عناوين مختلفة (قد تكون مواعيد مختلفة)")
            
            print()
        
        if not duplicates_found:
            print("✅ لا توجد مواعيد مشبوهة!")
        else:
            print("\n" + "="*70)
            print("❓ ما الذي تريد فعله؟")
            print("="*70)
            print("\n1. عرض خيارات الحذف")
            print("2. إلغاء")
            
            choice = input("\n👉 اختيارك: ").strip()
            
            if choice == '1':
                delete_menu(conn, by_time)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


def delete_menu(conn, by_time):
    """قائمة حذف المواعيد"""
    print("\n" + "="*70)
    print("🗑️ حذف مواعيد محددة")
    print("="*70)
    
    all_apts = []
    for time, apts in sorted(by_time.items()):
        all_apts.extend(apts)
    
    print("\n📋 جميع المواعيد:")
    for i, apt in enumerate(all_apts, 1):
        time = apt['date_time'].split(' ')[1][:5]
        print(f"{i}. [{time}] {apt['title']} (ID: {apt['id']})")
    
    print("\n💡 كيف تريد الحذف؟")
    print("1. اختيار أرقام محددة (مثال: 1,3,5)")
    print("2. حذف كل المواعيد في وقت معين")
    print("3. إلغاء")
    
    choice = input("\n👉 اختيارك: ").strip()
    
    if choice == '1':
        numbers = input("\nأدخل أرقام المواعيد المراد حذفها (مفصولة بفواصل): ")
        try:
            indices = [int(n.strip()) - 1 for n in numbers.split(',')]
            ids_to_delete = [all_apts[i]['id'] for i in indices if 0 <= i < len(all_apts)]
            
            if ids_to_delete:
                print(f"\n⚠️ سيتم حذف {len(ids_to_delete)} موعد:")
                for apt_id in ids_to_delete:
                    apt = next(a for a in all_apts if a['id'] == apt_id)
                    print(f"   • {apt['title']}")
                
                confirm = input("\n❓ متأكد؟ (y/n): ").strip().lower()
                
                if confirm == 'y':
                    cursor = conn.cursor()
                    placeholders = ','.join('?' * len(ids_to_delete))
                    cursor.execute(f'DELETE FROM appointments WHERE id IN ({placeholders})', ids_to_delete)
                    conn.commit()
                    print(f"\n✅ تم حذف {len(ids_to_delete)} موعد!")
                else:
                    print("\n❌ تم الإلغاء")
            else:
                print("\n❌ أرقام غير صحيحة")
        
        except Exception as e:
            print(f"\n❌ خطأ: {e}")
    
    elif choice == '2':
        print("\n⏰ الأوقات المتاحة:")
        times = sorted(by_time.keys())
        for i, time in enumerate(times, 1):
            print(f"{i}. {time} ({len(by_time[time])} موعد)")
        
        time_choice = input("\n👉 اختر رقم الوقت: ").strip()
        try:
            time_idx = int(time_choice) - 1
            if 0 <= time_idx < len(times):
                selected_time = times[time_idx]
                apts_to_delete = by_time[selected_time]
                
                print(f"\n⚠️ سيتم حذف جميع المواعيد في {selected_time}:")
                for apt in apts_to_delete:
                    print(f"   • {apt['title']}")
                
                confirm = input("\n❓ متأكد؟ (y/n): ").strip().lower()
                
                if confirm == 'y':
                    cursor = conn.cursor()
                    ids = [a['id'] for a in apts_to_delete]
                    placeholders = ','.join('?' * len(ids))
                    cursor.execute(f'DELETE FROM appointments WHERE id IN ({placeholders})', ids)
                    conn.commit()
                    print(f"\n✅ تم حذف {len(ids)} موعد!")
                else:
                    print("\n❌ تم الإلغاء")
        except Exception as e:
            print(f"\n❌ خطأ: {e}")


def smart_deduplicate():
    """حذف ذكي للمكررات"""
    print("\n" + "="*70)
    print("🤖 حذف ذكي للمواعيد المكررة")
    print("="*70)
    
    db_path = "agent_data.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # البحث عن مواعيد متشابهة (نفس الوقت، عناوين متشابهة)
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                id, title, date_time, created_at
            FROM appointments
            WHERE date(date_time) = ?
            ORDER BY date_time, created_at DESC
        ''', (today,))
        
        appointments = cursor.fetchall()
        
        # تجميع حسب الوقت
        by_time = {}
        for apt in appointments:
            apt_id, title, date_time, created_at = apt
            time_key = date_time
            
            if time_key not in by_time:
                by_time[time_key] = []
            
            by_time[time_key].append({
                'id': apt_id,
                'title': title,
                'created_at': created_at
            })
        
        # البحث عن مكررات محتملة
        potential_duplicates = []
        
        for time_key, apts in by_time.items():
            if len(apts) > 1:
                # فحص التشابه في العناوين
                for i in range(len(apts)):
                    for j in range(i + 1, len(apts)):
                        title1 = apts[i]['title'].lower().strip()
                        title2 = apts[j]['title'].lower().strip()
                        
                        # فحص التشابه (يحتوي أحدهما على الآخر)
                        if title1 in title2 or title2 in title1:
                            potential_duplicates.append((apts[i], apts[j], time_key))
        
        if not potential_duplicates:
            print("\n✅ لا توجد مواعيد مكررة واضحة!")
            conn.close()
            return
        
        print(f"\n⚠️ وجدت {len(potential_duplicates)} زوج من المواعيد المتشابهة:\n")
        
        for i, (apt1, apt2, time_key) in enumerate(potential_duplicates, 1):
            print(f"{i}. في {time_key}:")
            print(f"   [أ] '{apt1['title']}' (ID: {apt1['id']}, أُنشئ: {apt1['created_at']})")
            print(f"   [ب] '{apt2['title']}' (ID: {apt2['id']}, أُنشئ: {apt2['created_at']})")
            print()
        
        print("💡 الحل المقترح: الاحتفاظ بالأحدث من كل زوج")
        
        confirm = input("\n❓ تطبيق الحذف الذكي؟ (y/n): ").strip().lower()
        
        if confirm == 'y':
            deleted_ids = []
            
            for apt1, apt2, time_key in potential_duplicates:
                # حذف الأقدم
                if apt1['created_at'] < apt2['created_at']:
                    deleted_ids.append(apt1['id'])
                else:
                    deleted_ids.append(apt2['id'])
            
            if deleted_ids:
                placeholders = ','.join('?' * len(deleted_ids))
                cursor.execute(f'DELETE FROM appointments WHERE id IN ({placeholders})', deleted_ids)
                conn.commit()
                print(f"\n✅ تم حذف {len(deleted_ids)} موعد مكرر!")
        else:
            print("\n❌ تم الإلغاء")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


def main():
    """البرنامج الرئيسي"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🔍 فحص تفصيلي للمواعيد المشبوهة                       ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print("الخيارات:")
    print("1. تحليل مفصل لمواعيد اليوم")
    print("2. حذف ذكي للمكررات")
    print("3. خروج")
    
    choice = input("\n👉 اختيارك: ").strip()
    
    if choice == '1':
        analyze_appointments()
    elif choice == '2':
        smart_deduplicate()
    else:
        print("\n👋 وداعاً!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم الإيقاف")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()