export function shortlistedEmailTemplate(jobTitle, company = '') {
  const subject = `Congratulations! You've Been Shortlisted for ${jobTitle}`;
  const body = `Dear {candidate_name},

We are pleased to inform you that after careful review of your application, you have been shortlisted for the position of ${jobTitle}${company ? ` at ${company}` : ''}.

Our team will reach out to you shortly with further details about the interview process.

Best regards,
Recruitment Team`;
  return { subject, body };
}

export function rejectedEmailTemplate(jobTitle, company = '') {
  const subject = `Application Update for ${jobTitle}`;
  const body = `Dear {candidate_name},

Thank you for your interest in the ${jobTitle} position${company ? ` at ${company}` : ''} and for taking the time to apply.

After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.

We encourage you to apply for future openings that match your skills and experience.

Best regards,
Recruitment Team`;
  return { subject, body };
}

export function personalizeTemplate(template, candidateName) {
  return template
    .replace(/\{candidate_name\}/g, candidateName)
    .replace(/\{name\}/g, candidateName);
}
