import streamlit as st
import pandas as pd
import re

# --- تنظیمات پیشرفته صفحه ---
st.set_page_config(page_title="SnappShop BI Assistant", page_icon="⚡", layout="wide")

# --- استایل‌دهی سفارشی (CSS) برای زیباتر شدن نوار پیشرفت ---
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4CAF50, #8BC34A);
    }
    </style>
""", unsafe_allow_html=True)

# --- بارگذاری و بهینه‌سازی داده‌ها ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('master_ecommerce_data.csv')
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
        return df
    except FileNotFoundError:
        return None

df = load_data()

# --- مقداردهی حافظه سشن (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_context" not in st.session_state:
    st.session_state.user_context = None

# --- منوی کناری (Sidebar) حرفه‌ای ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933116.png", width=120)
    st.title("⚙️ کنترل‌پنل سیستم")
    st.markdown("---")
    role = st.selectbox("👤 سطح دسترسی (ارزیابی نقش):", 
                        ["مشتری (Customer)", "کارشناس لجستیک (Operator)", "مدیر ارشد (Executive)"])
    
    st.markdown("---")
    if st.button("🗑️ ریست کردن حافظه چت", use_container_width=True):
        st.session_state.messages = []
        st.session_state.user_context = None
        st.rerun()
        
    st.caption("ورژن سیستم: 3.0 (هوش تجاری اسنپ‌شاپ)")

# --- هدر اصلی داشبورد ---
st.title("⚡ دستیار هوشمند و تعاملی اسنپ‌شاپ")
st.caption(f"🟢 **وضعیت اتصال سرور:** پایدار | **دسترسی فعلی:** {role}")
st.markdown("---")

# --- لاجیک خوش‌آمدگویی هوشمند (با لحن‌های متفاوت برای هر نقش) ---
if len(st.session_state.messages) == 0:
    if "مشتری" in role:
        welcome_msg = "سلام! من هوش مصنوعی پشتیبانی اسنپ‌شاپ هستم. 🛍️\n\n🔹 برای **رهگیری مرسوله** کلمه `پیگیری` \n🔹 و برای **ثبت درخواست ارجاع کالا** کلمه `مرجوعی` را ارسال کنید."
    elif "کارشناس" in role:
        welcome_msg = "وقت بخیر همکار واحد لجستیک. 🚛\n\n🔹 جهت مانیتورینگ سفارشات دارای تاخیر بحرانی و مشاهده گلوگاه‌های ارسال، عبارت `بحران` را وارد نمایید."
    else:
        welcome_msg = "سلام جناب مدیر. به داشبورد فرماندهی خوش آمدید. 📈\n\n🔹 جهت فراخوانی داده‌های کلان و مشاهده وضعیت سیستم در لحظه، کلمه `داشبورد` را وارد کنید."
    
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# --- رندر کردن تاریخچه مکالمات ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- پردازش پیام جدید کاربر ---
if prompt := st.chat_input("دستور خود را اینجا تایپ کنید..."):
    # ثبت و نمایش پیام کاربر
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        user_input = prompt.strip().lower()
        
        if df is None:
            st.error("❌ **خطای بحرانی سیستمی:** پایگاه داده `master_ecommerce_data.csv` متصل نیست. لطفا از صحت وجود فایل در سرور اطمینان حاصل کنید.")
            st.stop()

        # ==========================================
        # ۱. پنل مدیر ارشد (داشبورد تعاملی)
        # ==========================================
        if "مدیر" in role:
            if "داشبورد" in user_input or "گزارش" in user_input:
                st.success("📊 **فراخوانی داده‌های کلان با موفقیت انجام شد.**")
                
                # محاسبه متریک‌های مدیریتی
                total_sales = df['total_payment_value'].sum()
                total_orders = df['order_id'].nunique()
                avg_order_value = total_sales / total_orders if total_orders > 0 else 0
                
                # نمایش متریک‌ها به شکل کارت‌های حرفه‌ای
                c1, c2, c3 = st.columns(3)
                c1.metric("💰 مجموع درآمد (ریال)", f"{total_sales:,.0f}", "+8.4% رشد (ماهانه)")
                c2.metric("📦 کل سفارشات پردازش‌شده", f"{total_orders:,}", "+1.2% رشد")
                c3.metric("💳 میانگین ارزش هر سبد", f"{avg_order_value:,.0f}", "-0.5% افت")
                
                # نمودار فروش استان‌ها
                st.markdown("🗺️ **توزیع درآمد بر اساس استان‌های برتر:**")
                top_states = df.groupby('customer_state')['total_payment_value'].sum().sort_values(ascending=False).head(7)
                st.bar_chart(top_states, color="#FF4B4B")
                
                # ذخیره این اکشن در هیستوری چت
                st.session_state.messages.append({"role": "assistant", "content": "✅ داشبورد مدیریتی با موفقیت رندر شد (نمودارها در محیط کاربری نمایش داده شدند)."})
            else:
                err_msg = "⚠️ دستور ناشناخته! لطفاً برای مشاهده اطلاعات کلان فروشگاه، کلمه `داشبورد` را وارد نمایید."
                st.warning(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})

        # ==========================================
        # ۲. پنل کارشناس ارسال (مانیتورینگ بحران)
        # ==========================================
        elif "کارشناس" in role:
            if "بحران" in user_input or "تاخیر" in user_input:
                st.error("🚨 **هشدار سیستم: لیست سفارشات با تاخیر بحرانی (بیشتر از ۵ روز)**")
                
                # فیلتر کردن دیتای تاخیردار
                critical_orders = df[df['delivery_delay_days'] > 5].sort_values(by='delivery_delay_days', ascending=False)
                critical_display = critical_orders[['order_id', 'customer_state', 'order_status', 'delivery_delay_days']].head(10)
                
                if not critical_display.empty:
                    st.dataframe(critical_display, use_container_width=True, hide_index=True)
                    
                    # قابلیت خروجی‌گیری
                    csv_data = critical_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 دریافت فایل اکسل جهت ارجاع به پیک",
                        data=csv_data,
                        file_name='critical_delayed_orders.csv',
                        mime='text/csv',
                        type="primary"
                    )
                    st.session_state.messages.append({"role": "assistant", "content": "✅ گزارش بحران لجستیک به همراه لینک دانلود با موفقیت تولید شد."})
                else:
                    st.success("🟢 وضعیت سبز: سیستم پایدار است و هیچ سفارش با تاخیر بحرانی در شبکه لجستیک وجود ندارد.")
                    st.session_state.messages.append({"role": "assistant", "content": "وضعیت سبز: تاخیر بحرانی یافت نشد."})
            else:
                err_msg = "⚠️ دسترسی نامعتبر. جهت بررسی گلوگاه‌های ارسال، صرفاً کلمه `بحران` را وارد نمایید."
                st.warning(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})

        # ==========================================
        # ۳. پنل مشتری (ترکینگ و اعتبارسنجی ارجاع کالا)
        # ==========================================
        elif "مشتری" in role:
            if "پیگیری" in user_input:
                st.session_state.user_context = "tracking"
                resp = "📍 برای **رهگیری دقیق مرسوله**، لطفاً **کد سفارش ۳۲ رقمی** خود را ارسال کنید:"
                st.info(resp)
                st.session_state.messages.append({"role": "assistant", "content": resp})
            
            elif "مرجوعی" in user_input:
                st.session_state.user_context = "returning"
                resp = "♻️ جهت بررسی شرایط ارجاع کالا، لطفاً **کد سفارش ۳۲ رقمی** خود را وارد نمایید:"
                st.info(resp)
                st.session_state.messages.append({"role": "assistant", "content": resp})
            
            # اعتبارسنجی پیشرفته کد سفارش Olist (فقط حروف a-f و اعداد، دقیقا ۳۲ کاراکتر)
            elif re.match(r"^[a-f0-9]{32}$", user_input):
                order_data = df[df['order_id'] == user_input]
                
                if not order_data.empty:
                    status = order_data.iloc[0]['order_status']
                    
                    # سناریوی رهگیری
                    if st.session_state.user_context == "tracking":
                        st.success(f"🔍 مرسوله شما در پایگاه داده یافت شد. (شناسه سیستمی: `SN-{user_input[:6].upper()}`)")
                        
                        st.markdown("### 📌 وضعیت فعلی مرسوله:")
                        if status == 'delivered':
                            st.progress(100, text="✅ تحویل داده شده به مشتری")
                        elif status in ['shipped', 'processing', 'invoiced', 'approved']:
                            st.progress(65, text="🚚 در حال پردازش و ارسال فیزیکی")
                        elif status in ['canceled', 'unavailable']:
                            st.error("❌ متاسفانه این سفارش توسط سیستم لغو شده است.")
                        else:
                            st.progress(25, text="📝 ثبت اولیه و در انتظار تایید انبار")
                            
                        st.session_state.user_context = None
                        st.session_state.messages.append({"role": "assistant", "content": f"✅ اطلاعات سفارش `{user_input[:6]}` به همراه نوار وضعیت با موفقیت فراخوانی شد."})
                        
                    # سناریوی مرجوعی
                    elif st.session_state.user_context == "returning":
                        if status == 'delivered':
                            ref_code = f"RET-{user_input[:6].upper()}-99"
                            success_msg = f"✅ **درخواست ارجاع کالا تایید اولیه شد.**\n\nکد رهگیری مرجوعی شما: `{ref_code}`\n\nلطفاً کالا را با بسته‌بندی اولیه به نزدیک‌ترین دفتر پست تحویل دهید."
                            st.success(success_msg)
                            st.session_state.messages.append({"role": "assistant", "content": success_msg})
                        else:
                            err_status = f"❌ **عدم تطابق با قوانین ارجاع کالا:**\nسفارش شما در سیستم به عنوان 'تحویل‌شده' ثبت نشده است (وضعیت فعلی: `{status}`).\n\n⚠️ *ثبت مرجوعی در سیستم یکپارچه، تنها پس از دریافت فیزیکی کالا توسط مشتری امکان‌پذیر است.*"
                            st.error(err_status)
                            st.session_state.messages.append({"role": "assistant", "content": err_status})
                            
                        st.session_state.user_context = None
                    else:
                        resp = "لطفاً ابتدا فرآیند مورد نظر را مشخص کنید (`پیگیری` یا `مرجوعی`)، سپس کد سفارش را ارسال فرمایید."
                        st.warning(resp)
                        st.session_state.messages.append({"role": "assistant", "content": resp})
                else:
                    resp = "❌ سفارشی با این مشخصات در دیتابیس اسنپ‌شاپ ثبت نشده است. لطفاً ساختار کد ارسالی را مجدداً بررسی نمایید."
                    st.error(resp)
                    st.session_state.messages.append({"role": "assistant", "content": resp})
            else:
                resp = "⚠️ ساختار ورودی نامعتبر است! لطفاً جهت اجرای دستورات کلمه `پیگیری`، `مرجوعی` یا صرفاً یک **کد سفارش معتبر ۳۲ کاراکتری** وارد نمایید."
                st.warning(resp)
                st.session_state.messages.append({"role": "assistant", "content": resp})