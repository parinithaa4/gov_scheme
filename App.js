import { useState } from "react";
import LanguageSelection from "./pages/LanguageSelection";
import AuthPage from "./pages/AuthPage";
import UserDetailsForm from "./pages/UserDetailsForm";
import ResultsPage from "./pages/ResultsPage";
import Chatbot from "./components/Chatbot";
import IndiaMapScene from "./components/IndiaMapScene";

function App() {
  const [step, setStep] = useState("language");
  const [lang, setLang] = useState("en");
  const [eligibilityData, setEligibilityData] = useState(null);
  const [user, setUser] = useState(null);

  return (
    <div className="app">
      <IndiaMapScene />

      <div className="content">
        {step !== "language" && (
          <h2 className="top-header">Welfare Scheme Recommendation Portal</h2>
        )}

        {step === "language" && (
          <LanguageSelection onNext={(l) => { setLang(l); setStep("auth"); }} />
        )}

        {step === "auth" && (
          <AuthPage onNext={() => {
  setUser({ name: "Demo User" });
  setStep("form");
}} />
        )}

        {step === "form" && (
          <UserDetailsForm
 onSubmit={(formData) => {
  const fakeResponse = {
    matching_schemes: [
      {
        name: "PM Awas Yojana",
        match_percentage: formData.income < 200000 ? "95%" : "70%",
        category: "Housing",
        description: "Affordable housing scheme",
        benefits: "Subsidy",
        eligibility: "Income based"
      }
    ],
    ai_recommendation: `Based on your income (${formData.income}), you are eligible for housing benefits.`
  };

  setEligibilityData(fakeResponse);
  setStep("results");
}}
          />
        )}

        {step === "results" && (
          <ResultsPage data={eligibilityData} />
        )}

        {step !== "language" && step !== "auth" && <Chatbot />}
      </div>
    </div>
  );
}

export default App;