import { useState, useEffect } from "react";

export default function UserDetailsForm({ onSubmit }) {
  const questions = [
    "Select your Date of Birth",
    "Select your Gender",
    "Enter your Occupation",
    "Enter your Monthly Income",
    "Select your State"
  ];

  const keys = ["dob", "gender", "occupation", "income", "state"];

  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [input, setInput] = useState("");
  const [displayedText, setDisplayedText] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const text = questions[step];
    if (!text) return;

    let i = 0;
    setDisplayedText("");

    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayedText(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 30);

    return () => clearInterval(interval);
  }, [step]);

  // 🔥 Calculate age
  const calculateAge = (dob) => {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const month = today.getMonth() - birthDate.getMonth();
    if (month < 0 || (month === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const handleNext = (value) => {
    if (!value) return;

  // 🔥 AGE VALIDATION (DOB step)
  if (step === 0) {
    const age = calculateAge(value);
    if (age < 0) {
      alert("Age cannot be negative");
      return;
    }
  }

  // 🔥 INCOME VALIDATION
  if (step === 3) {
    if (Number(value) < 0) {
      alert("Income cannot be negative");
      return;
    }
  }
  const newData = { ...answers, [keys[step]]: value };
    // 🔥 LAST STEP → FAKE BACKEND
    if (step === questions.length - 1) {
      setLoading(true);

      const age = calculateAge(newData.dob);

      setTimeout(() => {
        const fakeResponse = {
          matching_schemes: [
            {
              name: "PM Awas Yojana",
              match_percentage: age > 18 ? "90%" : "60%",
              category: "Housing",
              description: "Affordable housing support",
              benefits: "Loan subsidy",
              eligibility: "Income-based"
            },
            {
              name: "Skill Development Scheme",
              match_percentage:
                newData.occupation === "student" ? "95%" : "75%",
              category: "Education",
              description: "Skill training programs",
              benefits: "Free training",
              eligibility: "Youth & students"
            }
          ],
          ai_recommendation: `Based on your profile (${newData.occupation}, ₹${newData.income}), these schemes fit you best.`
        };

        setLoading(false);
        onSubmit(fakeResponse);
      }, 1000);
    } else {
      setAnswers(newData);
      setStep(step + 1);
      setInput("");
    }
  };

  const handleBack = () => {
    if (step === 0) return;

    const prevStep = step - 1;
    setStep(prevStep);

    const prevKey = keys[prevStep];
    setInput(answers[prevKey] || "");
  };

  return (
    <div className="card step-container">
      <h3 className="typing">{displayedText}</h3>

      {/* DOB */}
      {step === 0 && (
        <input
          type="date"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
      )}

      {/* Gender */}
      {step === 1 && (
        <select
          value={input}
          onChange={(e) => handleNext(e.target.value)}
        >
          <option value="">Select Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
      )}

      {/* Occupation */}
      {step === 2 && (
        <div className="grid">
          {[
            { label: "🎓 Student", value: "student" },
            { label: "🚀 Entrepreneur", value: "entrepreneur" },
            { label: "🧑‍💼 Self Employed", value: "self_employed" },
            { label: "🏢 Private Employee", value: "private_employee" },
            { label: "🏛️ Government Employee", value: "government_employee" },
            { label: "🌾 Farmer", value: "farmer" },
            { label: "🛠️ Daily Wage", value: "daily_wage_worker" },
            { label: "🏪 Business Owner", value: "business_owner" },
            { label: "🏠 Homemaker", value: "homemaker" },
            { label: "🧓 Retired", value: "retired" }
          ].map((item) => (
            <button
              key={item.value}
              className="option-btn"
              onClick={() => handleNext(item.value)}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}

      {/* Income */}
      {step === 3 && (
        <input
          type="number"
          placeholder="Income in ₹"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleNext(input)}
        />
      )}

      {/* State */}
      {step === 4 && (
        <select
          value={input}
          onChange={(e) => handleNext(e.target.value)}
        >
          <option value="">Select State</option>
          <option value="tamil_nadu">Tamil Nadu</option>
          <option value="kerala">Kerala</option>
          <option value="karnataka">Karnataka</option>
          <option value="delhi">Delhi</option>
          <option value="uttar_pradesh">Uttar Pradesh</option>
          <option value="maharashtra">Maharashtra</option>
        </select>
      )}

      {/* Buttons */}
      <div className="btn-row">
        {step > 0 && (
          <button className="back-btn" onClick={handleBack}>
            ⬅️
          </button>
        )}

        {(step !== 1 && step !== 4) && (
          <button
            className="next-btn"
            disabled={!input || loading}
            onClick={() => handleNext(input)}
          >
            {loading ? "..." : "➡️"}
          </button>
        )}
      </div>

      <p className="progress">
        Step {step + 1} / {questions.length}
      </p>
    </div>
  );
}