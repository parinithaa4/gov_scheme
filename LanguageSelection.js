export default function LanguageSelection({ onNext }) {
  return (
    <>
      {/* 🔥 Page Heading */}
      <h1 className="main-heading">
        Welcome to Welfare Scheme Recommendation Portal
      </h1>

      {/* 🔹 Card */}
      <div className="card">
        <h2>Select Language</h2>

        <button onClick={() => onNext("en")}>English</button>
        <button onClick={() => onNext("ta")}>தமிழ்</button>
        <button onClick={() => onNext("hi")}>हिंदी</button>
        <button onClick={() => onNext("te")}>తెలుగు</button>
        <button onClick={() => onNext("ml")}>മലയാളം</button>
      </div>
    </>
  );
}