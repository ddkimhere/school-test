module.exports = function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  return res.status(200).json({
    ok: true,
    model: 'gemini-3.5-flash-lite',
    keyConfigured: Boolean(process.env.GEMINI_API_KEY)
  });
};
