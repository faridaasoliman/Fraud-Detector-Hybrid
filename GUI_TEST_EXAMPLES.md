# Fraud Detector GUI - Test Input Examples

## Overview
Below are curated example inputs for testing the Fraud Detection GUI. The examples include typical legitimate transactions and patterns that are likely to be flagged as fraudulent.

---

## ✅ LEGITIMATE (Non-Fraud) Examples

### Example 1: Small Daily Purchase
```
Amount: 50.00
Time: 06:00
Country: US
MerchantCategory: Food
TransactionType: POS
Device: Mobile
CardType: Credit
PreviousFraudHistory: ✗ (unchecked)
```
**Expected Result:** NO FRAUD DETECTED (very low probability)

---

### Example 2: Regular Online Shopping
```
Amount: 125.50
Time: 43200  (12:00 PM)
Country: UK
MerchantCategory: Electronics
TransactionType: Online
Device: Desktop
CardType: Debit
PreviousFraudHistory: ✗ (unchecked)
```
**Expected Result:** NO FRAUD DETECTED (low probability)

---

### Example 3: Moderate ATM Withdrawal
```
Amount: 200.00
Time: 36000  (10:00 AM)
Country: DE
MerchantCategory: Luxury
TransactionType: ATM
Device: POS
CardType: Credit
PreviousFraudHistory: ✗ (unchecked)
```
**Expected Result:** NO FRAUD DETECTED (low probability)

---

### Example 4: Standard Online Transfer
```
Amount: 300.00
Time: 64800  (6:00 PM)
Country: FR
MerchantCategory: OnlineServices
TransactionType: Transfer
Device: Desktop
CardType: Virtual
PreviousFraudHistory: ✗ (unchecked)
```
**Expected Result:** NO FRAUD DETECTED (moderate probability, but safe)

---

## 🚨 SUSPICIOUS/FRAUD EXAMPLES

### Example 5: High-Risk Fraud Pattern #1
```
Amount: 500.00
Time: 02:40
Country: CN
MerchantCategory: Luxury
TransactionType: Online
Device: Mobile
CardType: Virtual
PreviousFraudHistory: ✓ (checked)
```
**Expected Result:** FRAUD DETECTED (high probability)

**Why it's flagged:**
- High amount ($500) for luxury purchase
- Early morning transaction time (unusual)
- Virtual card (higher risk)
- Previous fraud history increases likelihood
- Mobile device (easier to compromise)

---

### Example 6: High-Risk Fraud Pattern #2
```
Amount: 650.00
Time: 48000  (evening)
Country: IN
MerchantCategory: Electronics
TransactionType: Transfer
Device: Mobile
CardType: Virtual
PreviousFraudHistory: ✓ (checked)
```
**Expected Result:** FRAUD DETECTED (high probability)

**Why it's flagged:**
- Very high amount ($650)
- Virtual card used (higher risk indicator)
- Transfer type (funds moving out)
- Previous fraud history
- Mobile device usage

---

### Example 7: Suspicious Mid-Range Transaction
```
Amount: 400.00
Time: 3761  (very early morning ~1:03 AM)
Country: CN
MerchantCategory: OnlineServices
TransactionType: Online
Device: Mobile
CardType: Virtual
PreviousFraudHistory: ✓ (checked)
```
**Expected Result:** FRAUD DETECTED (high probability)

**Why it's flagged:**
- Abnormal time (very early morning)
- High amount for online services
- Multiple risk factors combined
- Virtual card + Mobile device

---

### Example 8: Moderate Fraud Indicator
```
Amount: 350.00
Time: 15000  (4:10 AM - early morning)
Country: EG
MerchantCategory: Luxury
TransactionType: Online
Device: Mobile
CardType: Credit
PreviousFraudHistory: ✓ (checked)
```
**Expected Result:** FRAUD DETECTED (moderate-to-high probability)

**Why it's flagged:**
- Unusual time (early morning)
- Luxury purchase at odd hour
- Previous fraud history

---

## 📊 Edge Case Examples

### Example 9: High Amount but Legitimate
```
Amount: 900.00
Time: 43200  (12:00 PM - noon)
Country: US
MerchantCategory: Electronics
TransactionType: Online
Device: Desktop
CardType: Credit
PreviousFraudHistory: ✗ (unchecked)
```
**Expected Result:** Likely NO FRAUD (reasonable time, no prior history, legitimate pattern)

---

### Example 10: Small Amount but Suspicious Pattern
```
Amount: 75.00
Time: 7200  (2:00 AM)
Country: CN
MerchantCategory: Luxury
TransactionType: Transfer
Device: Mobile
CardType: Virtual
PreviousFraudHistory: ✓ (checked)
```
**Expected Result:** FRAUD DETECTED (suspicious pattern indicators)

**Why it's flagged:**
- Multiple fraud indicators despite lower amount
- Odd transaction time
- Virtual card + Mobile
- Previous fraud history

---

## 🎯 Quick Testing Checklist

| Example | Type | Expected | Notes |
|---------|------|----------|-------|
| #1 | Legit | ✓ No Fraud | Small, normal time, no history |
| #2 | Legit | ✓ No Fraud | Standard online shopping |
| #3 | Legit | ✓ No Fraud | Normal ATM withdrawal |
| #4 | Legit | ✓ No Fraud | Standard transfer, reasonable time |
| #5 | Fraud | 🚨 Fraud | High amount, odd time, virtual card, history |
| #6 | Fraud | 🚨 Fraud | Very high, transfer, virtual, history |
| #7 | Fraud | 🚨 Fraud | Very early morning, high amount |
| #8 | Fraud | 🚨 Fraud | Early morning luxury, history |
| #9 | Edge | ✓ Likely Legit | High amount but clean pattern |
| #10 | Edge | 🚨 Fraud | Low amount but multiple red flags |

---

## 💡 Key Fraud Indicators Used by Model

Based on the training data patterns, the model likely considers:

1. **Amount**: Fraud cases average ~$300 (vs ~$160 for legitimate)
2. **Time**: Unusual hours (very early morning or late night)
3. **Country**: Higher risk from certain regions (CN, IN, EG)
4. **Card Type**: Virtual cards have higher fraud rate
5. **Device**: Mobile devices may have higher risk
6. **Transaction Type**: Transfer operations more risky
7. **Merchant Category**: Luxury, Electronics, OnlineServices higher risk
8. **Previous Fraud History**: Strong indicator (70% of fraud cases have this)

---

## 🧪 Testing Instructions

1. **Test Legitimate Cases First** (#1-4)
   - Verify green "✓ NO FRAUD DETECTED" message appears
   - Probability ring should be low (< 50%)

2. **Test Fraud Cases** (#5-8)
   - Verify red "⚠️ FRAUD DETECTED" message appears
   - Probability ring should be high (> 50%)

3. **Test Edge Cases** (#9-10)
   - Verify model behavior with conflicting signals
   - Check if GUI updates correctly

4. **Manual Testing**
   - Mix and match features to understand model behavior
   - Try extreme values (very high/low amounts)
   - Experiment with different time values

---

## 📝 Notes

- **Time values**: Use HH:MM format (24-hour clock)
  - 00:00 = midnight
  - 06:00 = 6 AM
  - 12:00 = noon
  - 18:00 = 6 PM
  - 23:59 = almost midnight
  - Examples: "02:40", "11:52", "14:39", "23:08"

- **Dataset countries**: AE, CN, DE, EG, FR, IN, UK, US

- **Merchant categories**: Clothing, Electronics, Food, Gaming, Gas, Luxury, OnlineServices, Travel

- **Transaction types**: ATM, Online, POS, Transfer

- **Devices**: Desktop, Mobile, POS, Tablet

- **Card types**: Credit, Debit, Virtual
