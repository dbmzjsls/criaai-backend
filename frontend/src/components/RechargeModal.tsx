import { useState, useEffect, useCallback, useId } from "react";
import { motion, AnimatePresence } from "framer-motion";

// ============================================================
// Type Definitions
// ============================================================

type PaymentMethod = "wechat" | "alipay";

type FlowStage = "select" | "loading" | "success";

interface RechargeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (amount: number) => void;
}

// ============================================================
// Constants
// ============================================================

const PRESET_AMOUNTS = [30, 50, 100, 200] as const;
const AMOUNT_RANGE = { min: 1, max: 5000 } as const;

/** 微噪点纹理 — SVG feTurbulence 叠加层，模拟真实材质表面微观颗粒 */
const NOISE_OVERLAY = `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E")`;

/** 物理弹簧曲线 — 模拟真实弹性形变 */
const SPRING_FAST = { type: "spring" as const, stiffness: 800, damping: 30 };
const SPRING_BOUNCE = { type: "spring" as const, stiffness: 500, damping: 22 };

// ============================================================
// Shared style presets (applied via inline style)
// ============================================================

/** 暗色磨砂金属 — 左上45°光源，内阴影模拟物理凹陷/凸起 */
const metalUnselected = {
  background: `
    linear-gradient(145deg, #3e3e4c 0%, #282836 55%, #1e1e2a 100%)
  `,
  border: "1px solid rgba(255,255,255,0.07)",
  boxShadow: `
    2px 2px 5px rgba(0,0,0,0.25),
    inset -2px -2px 4px rgba(255,255,255,0.03),
    inset 2px 2px 5px rgba(0,0,0,0.2)
  `,
  borderRadius: "12px",
  position: "relative" as const,
} as const;

/** 选中态 — 紫色调金属，光源逻辑保持一致，暗面加深 */
const metalSelected = {
  background: `
    linear-gradient(145deg, #575080 0%, #3b3565 55%, #2a2550 100%)
  `,
  border: "1px solid rgba(167,139,250,0.25)",
  boxShadow: `
    2px 2px 5px rgba(99,80,200,0.25),
    0 0 18px rgba(124,58,237,0.18),
    inset -2px -2px 5px rgba(200,180,255,0.06),
    inset 2px 2px 6px rgba(0,0,0,0.3)
  `,
  borderRadius: "12px",
  position: "relative" as const,
} as const;

/** 哑光玻璃 — backdrop-blur + 极低不透明度背景 */
const glassUnselected = {
  background: "rgba(255,255,255,0.04)",
  border: "1px solid rgba(255,255,255,0.10)",
  backdropFilter: "blur(12px)",
  WebkitBackdropFilter: "blur(12px)",
  borderRadius: "12px",
} as const;

const glassSelected = {
  background: "rgba(139,92,246,0.12)",
  border: "1px solid rgba(167,139,250,0.25)",
  backdropFilter: "blur(12px)",
  WebkitBackdropFilter: "blur(12px)",
  boxShadow: "0 0 18px rgba(124,58,237,0.12)",
  borderRadius: "12px",
} as const;

/** 确认按钮 — 深色金属底 + 紫色环境光 */
const confirmButton = {
  background: `
    linear-gradient(145deg, #4e4680 0%, #352d62 55%, #261f4a 100%)
  `,
  border: "1px solid rgba(167,139,250,0.2)",
  boxShadow: `
    2px 3px 8px rgba(99,80,200,0.2),
    inset -2px -2px 5px rgba(200,180,255,0.04),
    inset 2px 2px 6px rgba(0,0,0,0.25)
  `,
  borderRadius: "12px",
  color: "rgba(255,255,255,0.92)",
  fontWeight: 600,
  fontSize: "0.875rem",
  letterSpacing: "0.02em",
} as const;

/** 成功页 - 次要按钮 (金属质地) */
const secondaryButton = {
  ...metalUnselected,
  color: "rgba(255,255,255,0.7)",
  fontWeight: 600,
  fontSize: "0.875rem",
} as const;

/** 成功页 - 主按钮 (金属 + 紫色倾向) */
const primaryButton = {
  ...confirmButton,
} as const;

// ============================================================
// Sub-components
// ============================================================

const WechatIcon = ({ className = "" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M8.69 3.46c-3.86 0-7 2.82-7 6.3 0 1.92 1 3.65 2.54 4.78l.64.37-.24.86-.77 2.24 2.44-1.23.74-.38.79.23c.53.14 1.08.22 1.65.22.29 0 .57-.02.85-.05a5.54 5.54 0 0 1-.43-2.14c0-3.12 2.85-5.66 6.35-5.66.14 0 .28 0 .42.01A6.44 6.44 0 0 0 8.69 3.46zm-1.37 5.04a.78.78 0 1 1 0-1.56.78.78 0 0 1 0 1.56zm4.24 0a.78.78 0 1 1 0-1.56.78.78 0 0 1 0 1.56z" />
    <path d="M16.98 12.22c-3.28 0-5.95 2.41-5.95 5.38s2.67 5.38 5.95 5.38c.5 0 .99-.06 1.48-.18l.63-.16.61.31c.67.34 1.45.74 1.98 1 .08.04.25-.05.22-.17l-.22-1.61-.07-.56.49-.42a4.99 4.99 0 0 0 1.75-3.8c0-2.96-2.67-5.37-5.96-5.37h-.02c-.28 0-.56.02-.84.05.06.29.1.58.1.88a5.54 5.54 0 0 1-.39 2.03.76.76 0 0 1 .04.24zm-2.24 2.6a.67.67 0 1 1 0-1.34.67.67 0 0 1 0 1.34zm3.66 0a.67.67 0 1 1 0-1.34.67.67 0 0 1 0 1.34z" />
  </svg>
);

const AlipayIcon = ({ className = "" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.2 7.5h-1.8c-.06.32-.14.63-.24.92h2.04v.82H7.7v-.82h3.08c-.04-.24-.07-.48-.08-.72H7.7V9.15h4.07c.02-.24.05-.46.1-.67H7.7v-.83h5.83c.55-.76 1.3-1.35 2.2-1.68l.57 1.01c-.65.25-1.22.65-1.69 1.16h1.59v.83h-1.52c.08.22.14.44.18.67h1.34v.86zM7.7 14.2h2.58c0 .9.55 1.56 1.37 1.87l-.46 1.07c-1.13-.44-2-.8-2-1.97H7.7v-.97zm4.8 0h1.6v.97h-1.6v-.97zm3.2 0h-1.6v.97h1.6v-.97zm-6.2 1.96h2.2c.23.38.57.67.98.84l-.46 1.05c-.68-.3-1.2-.68-1.6-1.17h-1.12v-.72zm4.6 0h4v.72h-4v-.72z" />
  </svg>
);

// ============================================================
// RechargeModal
// ============================================================

export default function RechargeModal({
  isOpen,
  onClose,
  onSuccess,
}: RechargeModalProps) {
  const [stage, setStage] = useState<FlowStage>("select");
  const [selectedAmount, setSelectedAmount] = useState<number>(30);
  const [customAmount, setCustomAmount] = useState<string>("");
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("wechat");
  const [validationError, setValidationError] = useState<string>("");
  /** 按压动画状态：null | "pressing" | "rebound" */
  const [pressingBtn, setPressingBtn] = useState<number | null>(null);

  const gradientId = useId();

  useEffect(() => {
    if (isOpen) {
      setStage("select");
      setSelectedAmount(30);
      setCustomAmount("");
      setPaymentMethod("wechat");
      setValidationError("");
    }
  }, [isOpen]);

  const finalAmount =
    customAmount !== "" ? parseInt(customAmount, 10) : selectedAmount;

  const handleClose = useCallback(() => {
    if (stage === "loading") return;
    onClose();
  }, [stage, onClose]);

  // ---- 金额选择 (带物理按压反馈) ----
  const handlePresetClick = (amount: number) => {
    // 物理按压序列：sink → rebound
    setPressingBtn(amount);
    setTimeout(() => setPressingBtn(null), 150);

    setSelectedAmount(amount);
    setCustomAmount("");
    setValidationError("");
  };

  const handleCustomInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === "") {
      setCustomAmount("");
      setValidationError("");
      return;
    }
    if (!/^\d+$/.test(raw)) return;

    const num = parseInt(raw, 10);
    if (num < AMOUNT_RANGE.min) {
      setValidationError(`最低充值 ${AMOUNT_RANGE.min} 元`);
    } else if (num > AMOUNT_RANGE.max) {
      setValidationError(`最高充值 ${AMOUNT_RANGE.max} 元`);
    } else {
      setValidationError("");
    }
    setCustomAmount(raw);
    setSelectedAmount(0);
  };

  // ---- 模拟充值提交 ----
  const handleSubmit = () => {
    if (customAmount !== "") {
      const num = parseInt(customAmount, 10);
      if (isNaN(num) || num < AMOUNT_RANGE.min || num > AMOUNT_RANGE.max) return;
    }
    setStage("loading");
    setTimeout(() => {
      setStage("success");
      onSuccess?.(finalAmount);
    }, 1500);
  };

  const handleRechargeAgain = () => {
    setStage("select");
    setSelectedAmount(30);
    setCustomAmount("");
    setPaymentMethod("wechat");
  };

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen && stage !== "loading") handleClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [isOpen, handleClose, stage]);

  // ============================================================
  // Render
  // ============================================================
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
          onClick={handleClose}
        >
          {/* 磨砂遮罩 */}
          <div className="absolute inset-0 bg-black/60 backdrop-blur-md" />

          {/* 弹窗主体 */}
          <motion.div
            className="relative w-full max-w-[400px] sm:w-[90%] rounded-2xl overflow-hidden"
            style={{
              background: `
                linear-gradient(165deg, rgba(28,25,58,0.97) 0%, rgba(18,17,35,0.99) 100%)
              `,
              border: "1px solid rgba(139,92,246,0.18)",
              boxShadow: `
                0 30px 70px rgba(0,0,0,0.55),
                0 0 100px rgba(124,58,237,0.10),
                inset 0 1px 0 rgba(255,255,255,0.03)
              `,
            }}
            initial={{ scale: 0.88, opacity: 0, y: 24 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.88, opacity: 0, y: 24 }}
            transition={SPRING_BOUNCE}
            onClick={(e) => e.stopPropagation()}
          >
            {/* 顶部金属嵌条 */}
            <div
              className="h-[2px] w-full"
              style={{
                background: `
                  linear-gradient(90deg,
                    transparent 0%,
                    rgba(167,139,250,0.5) 15%,
                    rgba(196,181,253,0.7) 40%,
                    rgba(167,139,250,0.5) 60%,
                    rgba(196,181,253,0.7) 85%,
                    transparent 100%
                  )
                `,
                boxShadow: "0 1px 4px rgba(124,58,237,0.15)",
              }}
            />

            {/* ======== 选择金额 ======== */}
            {stage === "select" && (
              <div className="p-6">
                {/* 标题 */}
                <div className="flex items-center justify-between mb-5">
                  <h2
                    className="text-base font-semibold tracking-wide"
                    style={{ color: "rgba(255,255,255,0.85)" }}
                  >
                    账户充值
                  </h2>
                  <button
                    onClick={handleClose}
                    className="w-7 h-7 flex items-center justify-center rounded-full"
                    style={{
                      background: "rgba(255,255,255,0.06)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      color: "rgba(255,255,255,0.45)",
                    }}
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* 预设金额 */}
                <p className="text-[10.5px] mb-3 tracking-widest uppercase" style={{ color: "rgba(255,255,255,0.3)" }}>
                  选择充值金额
                </p>
                <div className="grid grid-cols-4 gap-2.5 mb-4">
                  {PRESET_AMOUNTS.map((amount) => {
                    const isActive = customAmount === "" && selectedAmount === amount;
                    const isPressing = pressingBtn === amount;

                    return (
                      <motion.button
                        key={amount}
                        onClick={() => handlePresetClick(amount)}
                        className="relative py-3 text-sm font-semibold select-none overflow-hidden"
                        style={{
                          ...(isActive ? metalSelected : metalUnselected),
                          color: isActive ? "rgba(255,255,255,0.92)" : "rgba(255,255,255,0.55)",
                          // 物理按压：先下沉再回弹
                          transform: isPressing
                            ? "translateY(1.5px) scale(0.97)"
                            : "translateY(0) scale(1)",
                          transition: isPressing
                            ? "transform 0.08s ease-in"
                            : "transform 0.12s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
                        }}
                        whileHover={{
                          scale: 1.025,
                          transition: { duration: 0.2, ease: [0.175, 0.885, 0.32, 1.275] },
                        }}
                      >
                        {/* 噪点纹理层 */}
                        <div
                          className="absolute inset-0 pointer-events-none mix-blend-overlay"
                          style={{ backgroundImage: NOISE_OVERLAY, opacity: isActive ? 0.5 : 0.35 }}
                        />
                        {/* 左上高光 */}
                        <div
                          className="absolute top-[3px] left-[6px] right-[20%] h-px rounded-full pointer-events-none"
                          style={{
                            background: isActive
                              ? "linear-gradient(90deg, rgba(200,180,255,0.3), transparent)"
                              : "linear-gradient(90deg, rgba(255,255,255,0.12), transparent)",
                          }}
                        />
                        {/* 文字微沉压感 (选中态) */}
                        <span
                          className="relative inline-block"
                          style={isActive ? { top: "0.5px" } : undefined}
                        >
                          <span style={{ fontSize: "1.05em" }}>¥</span>
                          {amount}
                        </span>
                      </motion.button>
                    );
                  })}
                </div>

                {/* 自定义金额 */}
                <p className="text-[10.5px] mb-3 tracking-widest uppercase" style={{ color: "rgba(255,255,255,0.3)" }}>
                  自定义金额 (1-5000)
                </p>
                <div className="relative mb-5">
                  <span
                    className="absolute left-4 top-1/2 -translate-y-1/2 select-none"
                    style={{ color: "rgba(255,255,255,0.3)", fontSize: "1.05em" }}
                  >
                    ¥
                  </span>
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="输入充值金额"
                    value={customAmount}
                    onChange={handleCustomInput}
                    className="w-full pl-10 pr-4 py-3 text-sm outline-none text-white placeholder-current"
                    style={{
                      background: "rgba(255,255,255,0.04)",
                      border: validationError
                        ? "1px solid rgba(248,113,113,0.35)"
                        : "1px solid rgba(255,255,255,0.08)",
                      borderRadius: "12px",
                      color: "rgba(255,255,255,0.85)",
                      // 内嵌阴影模拟输入槽
                      boxShadow: "inset 2px 2px 5px rgba(0,0,0,0.2)",
                      transition: "border-color 0.2s ease",
                    }}
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = "rgba(139,92,246,0.4)";
                      e.currentTarget.style.boxShadow =
                        "inset 2px 2px 5px rgba(0,0,0,0.2), 0 0 0 3px rgba(124,58,237,0.08)";
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = validationError
                        ? "rgba(248,113,113,0.35)"
                        : "rgba(255,255,255,0.08)";
                      e.currentTarget.style.boxShadow = "inset 2px 2px 5px rgba(0,0,0,0.2)";
                    }}
                  />
                  {validationError && (
                    <motion.p
                      initial={{ opacity: 0, y: -4 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-1.5 ml-1"
                      style={{ color: "rgba(252,165,165,0.9)", fontSize: "0.75rem" }}
                    >
                      {validationError}
                    </motion.p>
                  )}
                </div>

                {/* 支付方式 */}
                <p className="text-[10.5px] mb-3 tracking-widest uppercase" style={{ color: "rgba(255,255,255,0.3)" }}>
                  支付方式
                </p>
                <div className="flex gap-2.5 mb-5">
                  {([
                    { key: "wechat", label: "微信支付", Icon: WechatIcon },
                    { key: "alipay", label: "支付宝", Icon: AlipayIcon },
                  ] as const).map(({ key, label, Icon }) => {
                    const isActive = paymentMethod === key;
                    return (
                      <motion.button
                        key={key}
                        whileHover={{
                          scale: 1.02,
                          transition: { duration: 0.2, ease: [0.175, 0.885, 0.32, 1.275] },
                        }}
                        whileTap={{ scale: 0.98, y: 1, transition: { duration: 0.08 } }}
                        onClick={() => setPaymentMethod(key)}
                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium select-none"
                        style={{
                          ...(isActive ? glassSelected : glassUnselected),
                          color: isActive
                            ? "rgba(255,255,255,0.88)"
                            : "rgba(255,255,255,0.4)",
                          transition: "all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
                        }}
                      >
                        <Icon
                          className="w-5 h-5"
                          style={{
                            color: isActive
                              ? key === "wechat"
                                ? "rgba(74,222,128,0.9)"
                                : "rgba(96,165,250,0.9)"
                              : "rgba(255,255,255,0.25)",
                          }}
                        />
                        {label}
                      </motion.button>
                    );
                  })}
                </div>

                {/* 确认充值按钮 */}
                <motion.button
                  whileHover={{
                    scale: 1.015,
                    transition: { duration: 0.2, ease: [0.175, 0.885, 0.32, 1.275] },
                  }}
                  whileTap={{
                    scale: 0.985,
                    y: 1.5,
                    transition: { duration: 0.08 },
                  }}
                  onClick={handleSubmit}
                  disabled={
                    customAmount !== "" &&
                    (parseInt(customAmount, 10) < AMOUNT_RANGE.min ||
                      parseInt(customAmount, 10) > AMOUNT_RANGE.max ||
                      isNaN(parseInt(customAmount, 10)))
                  }
                  className="relative w-full py-3.5 rounded-[12px] select-none overflow-hidden disabled:opacity-30 disabled:cursor-not-allowed"
                  style={confirmButton}
                >
                  {/* 噪点纹理 */}
                  <div
                    className="absolute inset-0 pointer-events-none mix-blend-soft-light"
                    style={{ backgroundImage: NOISE_OVERLAY, opacity: 0.4 }}
                  />
                  {/* 细微顶部高光 */}
                  <div
                    className="absolute top-[3px] left-[5%] right-[5%] h-px rounded-full pointer-events-none"
                    style={{
                      background: "linear-gradient(90deg, transparent, rgba(200,180,255,0.15), transparent)",
                    }}
                  />
                  <span className="relative">
                    确认充值 ¥{finalAmount || "—"}
                  </span>
                </motion.button>
              </div>
            )}

            {/* ======== 加载中 ======== */}
            {stage === "loading" && (
              <div className="p-10 flex flex-col items-center justify-center">
                {/* 脉冲呼吸圆环 (替代旋转spinner) */}
                <div className="relative mb-7">
                  {/* 固定底环 */}
                  <div
                    className="w-[68px] h-[68px] rounded-full"
                    style={{
                      border: "2px solid rgba(255,255,255,0.06)",
                    }}
                  />
                  {/* 呼吸动画圆环 */}
                  <motion.div
                    className="absolute inset-0 rounded-full"
                    style={{
                      border: "2px solid transparent",
                      borderTopColor: "rgba(139,92,246,0.6)",
                      borderRightColor: "rgba(139,92,246,0.3)",
                    }}
                    animate={{
                      scale: [1, 1.06, 1],
                      opacity: [0.5, 1, 0.5],
                    }}
                    transition={{
                      duration: 1.8,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />
                  {/* 内圈逆向脉冲 */}
                  <motion.div
                    className="absolute inset-[6px] rounded-full"
                    style={{
                      border: "1.5px solid transparent",
                      borderBottomColor: "rgba(167,139,250,0.5)",
                      borderLeftColor: "rgba(167,139,250,0.2)",
                    }}
                    animate={{
                      scale: [1, 0.94, 1],
                      opacity: [0.7, 1, 0.7],
                    }}
                    transition={{
                      duration: 1.8,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 0.4,
                    }}
                  />
                  {/* 中心金额 */}
                  <span
                    className="absolute inset-0 flex items-center justify-center text-xs font-bold"
                    style={{ color: "rgba(255,255,255,0.7)" }}
                  >
                    ¥{finalAmount}
                  </span>
                </div>

                {/* 按钮微脉动 */}
                <motion.div
                  className="px-10 py-3 rounded-[12px] text-sm font-medium select-none"
                  style={{
                    ...metalUnselected,
                    color: "rgba(255,255,255,0.55)",
                    textAlign: "center",
                  }}
                  animate={{
                    scale: [0.99, 1.008, 0.99],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
                  正在处理支付...
                </motion.div>
                <p className="text-[11px] mt-3" style={{ color: "rgba(255,255,255,0.2)" }}>
                  请稍候
                </p>
              </div>
            )}

            {/* ======== 充值成功 ======== */}
            {stage === "success" && (
              <div className="p-10 flex flex-col items-center justify-center">
                {/* 成功图标 — 绿色金属质感圆环 */}
                <motion.div
                  initial={{ scale: 0, rotate: -30 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={SPRING_FAST}
                  className="w-16 h-16 rounded-full flex items-center justify-center mb-5 relative"
                  style={{
                    background: `
                      linear-gradient(145deg, rgba(34,197,94,0.15), rgba(16,185,129,0.08))
                    `,
                    border: "1.5px solid rgba(34,197,94,0.35)",
                    boxShadow: `
                      0 0 28px rgba(34,197,94,0.12),
                      inset 0 1px 0 rgba(255,255,255,0.05)
                    `,
                  }}
                >
                  <svg
                    className="w-8 h-8"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="rgba(74,222,128,0.9)"
                    strokeWidth={2.5}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <motion.path
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ delay: 0.2, duration: 0.4 }}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </motion.div>

                <motion.h3
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-base font-semibold mb-1"
                  style={{ color: "rgba(255,255,255,0.85)" }}
                >
                  充值成功
                </motion.h3>
                <motion.p
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-sm mb-1"
                  style={{ color: "rgba(255,255,255,0.45)" }}
                >
                  已成功充值{" "}
                  <span className="font-bold" style={{ color: "rgba(255,255,255,0.85)" }}>
                    ¥{finalAmount}
                  </span>
                </motion.p>
                <motion.p
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-[11px] mb-6"
                  style={{ color: "rgba(255,255,255,0.2)" }}
                >
                  余额已即时到账
                </motion.p>

                {/* 操作按钮组 */}
                <div className="flex gap-2.5 w-full">
                  <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    onClick={handleRechargeAgain}
                    className="relative flex-1 py-3 rounded-[12px] select-none overflow-hidden"
                    style={secondaryButton}
                    whileHover={{ scale: 1.02, transition: { duration: 0.2, ease: [0.175, 0.885, 0.32, 1.275] } }}
                    whileTap={{ scale: 0.98, y: 1, transition: { duration: 0.08 } }}
                  >
                    <div
                      className="absolute inset-0 pointer-events-none mix-blend-overlay"
                      style={{ backgroundImage: NOISE_OVERLAY, opacity: 0.3 }}
                    />
                    <span className="relative">继续充值</span>
                  </motion.button>

                  <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.45 }}
                    onClick={handleClose}
                    className="relative flex-1 py-3 rounded-[12px] select-none overflow-hidden"
                    style={primaryButton}
                    whileHover={{ scale: 1.02, transition: { duration: 0.2, ease: [0.175, 0.885, 0.32, 1.275] } }}
                    whileTap={{ scale: 0.98, y: 1, transition: { duration: 0.08 } }}
                  >
                    <div
                      className="absolute inset-0 pointer-events-none mix-blend-soft-light"
                      style={{ backgroundImage: NOISE_OVERLAY, opacity: 0.35 }}
                    />
                    <div
                      className="absolute top-[3px] left-[8%] right-[8%] h-px rounded-full pointer-events-none"
                      style={{
                        background: "linear-gradient(90deg, transparent, rgba(200,180,255,0.15), transparent)",
                      }}
                    />
                    <span className="relative">完成</span>
                  </motion.button>
                </div>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
