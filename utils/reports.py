from utils.scoring import get_level, strength_and_weakness, next_challenge


def report_text(name, scores, profile, fields, growth=None, cluster_name=None):
    strength, weakness = strength_and_weakness(scores)

    lines = []
    lines.append(f"AM Report for {name}")
    lines.append("")
    lines.append(f"AM Profile: {profile}")
    if cluster_name:
        lines.append(f"ML Cluster: {cluster_name}")
    lines.append(f"Innovation Score: {scores['innovation_score']}/100 ({get_level(scores['innovation_score'])})")
    if growth is not None:
        sign = "+" if growth >= 0 else ""
        lines.append(f"Growth from last attempt: {sign}{growth}")
    lines.append("")
    lines.append("Score Breakdown")
    lines.append(f"Creativity: {scores['creativity']}")
    lines.append(f"Originality: {scores['originality']}")
    lines.append(f"Problem Solving: {scores['problem_solving']}")
    lines.append(f"Research Aptitude: {scores['research_aptitude']}")
    lines.append(f"Invention Thinking: {scores['invention_thinking']}")
    lines.append(f"Pattern Recognition: {scores['pattern_recognition']}")
    lines.append(f"Risk Taking: {scores['risk_taking']}")
    lines.append("")
    lines.append(f"Main Strength: {strength.capitalize()}")
    lines.append(f"Improvement Area: {weakness.capitalize()}")
    lines.append(f"Next Challenge: {next_challenge(weakness)}")
    lines.append("")
    lines.append("Recommended Fields")
    for f in fields:
        lines.append(f"- {f}")
    return "\n".join(lines)


def profile_explanation(profile):
    info = {
        "Research Explorer": "This type is strong at asking deeper questions, finding reasons and studying patterns before jumping to answers.",
        "Creative Inventor": "This type generates unusual ideas and can imagine new products or possibilities.",
        "Practical Problem Solver": "This type is good at breaking problems into practical steps and realistic solutions.",
        "Bold Experimenter": "This type is ready to try risky or original ideas and learn from failure.",
        "Product Builder": "This type thinks in terms of features, users and real-world usefulness.",
        "Growing Innovator": "This type is still developing but has potential that can improve with regular challenges."
    }
    return info.get(profile, "This profile shows a mixed thinking style.")
