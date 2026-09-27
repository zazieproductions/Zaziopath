import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont('Helvetica-Bold', 7.5)
        self.setFillColor(colors.HexColor('#0284c7'))
        
        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 756, 'RESTRICTED CASEFILE // ZP-2026-XRAY')
            self.setFont('Helvetica', 7.5)
            self.setFillColor(colors.HexColor('#64748b'))
            self.drawString(185, 756, '|   ANATOMIA CONTRADICTIONIS: FORENSIC RADIOGRAPHIC DOSSIER')
            self.drawRightString(612 - 36, 756, 'SUBJECT: ZAZIE KANWAR-TORGE')
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(36, 748, 612 - 36, 748)
        
        # Running footer
        self.setFont('Helvetica-Bold', 7)
        self.setFillColor(colors.HexColor('#dc2626'))
        self.drawString(36, 32, 'CONFIDENTIAL')
        self.setFont('Helvetica', 7)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawString(98, 32, '|   CONSULTING PSYCHIATRY: DR. H. LECTER & DR. B. DU MAURIER   |   PALAZZO CAPPONI')
        page_str = f'Page {self._pageNumber} of {page_count}'
        self.drawRightString(612 - 36, 32, page_str)
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(36, 42, 612 - 36, 42)
        self.restoreState()

def build_pdf(filename="ANATOMIA_CONTRADICTIONIS_LECTER_DUMAURIER_XRAY.pdf"):
    # Page dimensions: 612 x 792 pt. Margins: 36 pt left/right, 44 pt top/bottom. Printable width: 540 pt.
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=44,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    # Custom Typography Hierarchy
    c_slate900 = colors.HexColor('#0f172a')
    c_slate800 = colors.HexColor('#1e293b')
    c_slate700 = colors.HexColor('#334155')
    c_slate500 = colors.HexColor('#64748b')
    c_cyan600  = colors.HexColor('#0284c7')
    c_cyan700  = colors.HexColor('#0369a1')
    c_cyan400  = colors.HexColor('#38bdf8')
    c_amber800 = colors.HexColor('#92400e')
    c_rose900  = colors.HexColor('#881337')
    c_blue900  = colors.HexColor('#1e3a8a')
    c_red700   = colors.HexColor('#b91c1c')

    styles.add(ParagraphStyle('DocHeaderBanner', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=20, leading=23, textColor=c_slate900, alignment=1))
    styles.add(ParagraphStyle('DocSubtitle', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=c_cyan700, alignment=1))
    styles.add(ParagraphStyle('DocEpigraph', fontName='Times-Italic', fontSize=8.5, leading=12, textColor=c_slate700, alignment=1))
    
    styles.add(ParagraphStyle('SectionHead', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=c_slate900, keepWithNext=True))
    styles.add(ParagraphStyle('SectionSub', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=c_cyan600, keepWithNext=True))
    styles.add(ParagraphStyle('SubsectionHead', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=c_slate800, keepWithNext=True))
    
    styles.add(ParagraphStyle('BodyTextCustom', fontName='Helvetica', fontSize=8, leading=11.2, textColor=c_slate800))
    styles.add(ParagraphStyle('BodyTextCustomBold', fontName='Helvetica-Bold', fontSize=8, leading=11.2, textColor=c_slate900))
    styles.add(ParagraphStyle('BodyTextMuted', fontName='Helvetica', fontSize=7.5, leading=10, textColor=c_slate500))

    # Dramatic Dialogue Styles
    styles.add(ParagraphStyle('SpeakerLecter', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=c_rose900))
    styles.add(ParagraphStyle('DialogueLecter', fontName='Times-Italic', fontSize=8.5, leading=11.8, textColor=c_slate900))
    styles.add(ParagraphStyle('SpeakerDuMaurier', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=c_blue900))
    styles.add(ParagraphStyle('DialogueDuMaurier', fontName='Helvetica', fontSize=8, leading=11.2, textColor=c_slate900))
    styles.add(ParagraphStyle('NarrativeScene', fontName='Times-Italic', fontSize=7.5, leading=10.5, textColor=c_slate500))

    # Intake Table Styles
    styles.add(ParagraphStyle('IntakeLabel', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=c_slate700))
    styles.add(ParagraphStyle('IntakeVal', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=c_slate900))
    styles.add(ParagraphStyle('IntakeValBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=c_slate900))
    styles.add(ParagraphStyle('IntakeValMono', fontName='Courier', fontSize=7, leading=9, textColor=c_slate800))

    # X-Ray Scan Styles
    styles.add(ParagraphStyle('XRayBannerTitle', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=colors.white))
    styles.add(ParagraphStyle('XRayBannerMeta', fontName='Courier-Bold', fontSize=7, leading=9, textColor=c_cyan400, alignment=2))
    styles.add(ParagraphStyle('XRayHeadFlesh', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=c_slate700))
    styles.add(ParagraphStyle('XRayBodyFlesh', fontName='Helvetica', fontSize=7.5, leading=10.2, textColor=c_slate800))
    styles.add(ParagraphStyle('XRayHeadBone', fontName='Courier-Bold', fontSize=7.5, leading=9.5, textColor=c_slate900))
    styles.add(ParagraphStyle('XRayBodyBone', fontName='Courier', fontSize=7.2, leading=9.8, textColor=c_slate900))
    styles.add(ParagraphStyle('XRayHeadFracture', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=c_amber800))
    styles.add(ParagraphStyle('XRayBodyFracture', fontName='Helvetica-Bold', fontSize=7.5, leading=10.2, textColor=c_amber800))
    styles.add(ParagraphStyle('XRayHeadBedelia', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=c_blue900))
    styles.add(ParagraphStyle('XRayBodyBedelia', fontName='Helvetica', fontSize=7.5, leading=10.2, textColor=c_slate900))
    styles.add(ParagraphStyle('XRayHeadLecter', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=c_rose900))
    styles.add(ParagraphStyle('XRayBodyLecter', fontName='Times-Italic', fontSize=7.8, leading=10.5, textColor=c_slate900))

    # Matrix Table Styles
    styles.add(ParagraphStyle('MatHead', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle('MatCol1', fontName='Helvetica-Bold', fontSize=6.8, leading=8.5, textColor=c_slate900))
    styles.add(ParagraphStyle('MatCol2', fontName='Helvetica', fontSize=6.5, leading=8.2, textColor=c_slate700))
    styles.add(ParagraphStyle('MatCol3', fontName='Courier', fontSize=6.2, leading=8, textColor=c_slate800))
    styles.add(ParagraphStyle('MatCol4', fontName='Helvetica-Bold', fontSize=6.5, leading=8.2, textColor=c_amber800))
    styles.add(ParagraphStyle('MatCol5', fontName='Helvetica-Bold', fontSize=6.5, leading=8.2, textColor=c_red700, alignment=1))

    story = []

    # ==========================================
    # PAGE 1: COVER & FORENSIC INTAKE DOSSIER
    # ==========================================
    
    # Top banner
    top_banner_data = [[
        Paragraph("RESTRICTED FORENSIC ARCHIVE // PRIVILEGED CONSULTATION // DO NOT CIRCULATE", styles['DocHeaderBanner'])
    ]]
    top_banner_tab = Table(top_banner_data, colWidths=[540])
    top_banner_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_slate900),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(top_banner_tab)
    story.append(Spacer(1, 10))

    # Title & Subtitle
    story.append(Paragraph("ANATOMIA CONTRADICTIONIS", styles['DocTitle']))
    story.append(Paragraph("A FORENSIC RADIOGRAPHIC VIVISECTION OF ZAZIE KANWAR-TORGE", styles['DocSubtitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>Conducted by Dr. Hannibal Lecter & Dr. Bedelia Du Maurier · Palazzo Capponi, Florence</i>", styles['DocEpigraph']))
    story.append(Spacer(1, 10))

    # Forensic Intake Table
    intake_data = [
        [
            Paragraph("CASE REFERENCE", styles['IntakeLabel']),
            Paragraph("ZP-2026-XRAY / ZAZIOPATH DEEP RECURSION", styles['IntakeValMono']),
            Paragraph("CLASSIFICATION", styles['IntakeLabel']),
            Paragraph("LEVEL 4 SPECIAL DIAGNOSTIC", styles['IntakeValMono'])
        ],
        [
            Paragraph("SUBJECT IDENTITY", styles['IntakeLabel']),
            Paragraph("Zazie Kanwar-Torge (DOB: 2006-04-01, 8:55 PM, Age 20)", styles['IntakeVal']),
            Paragraph("LEGAL ENTITY", styles['IntakeLabel']),
            Paragraph("Zazie Productions LLC (NC Disregarded)", styles['IntakeVal'])
        ],
        [
            Paragraph("DIAGNOSTIC AXES", styles['IntakeLabel']),
            Paragraph("Autism Spectrum, ADHD, AvPD, Severe OCD, Bipolar (rem.)", styles['IntakeVal']),
            Paragraph("BASE OF OPS", styles['IntakeLabel']),
            Paragraph("Asheville, North Carolina (Domestic Perimeter)", styles['IntakeVal'])
        ],
        [
            Paragraph("PRIMARY DATASET", styles['IntakeLabel']),
            Paragraph("81 Root Files, 323 PDF pp, 200 Catalog Tracks, 604 Memory Lns", styles['IntakeVal']),
            Paragraph("REGISTRY CODES", styles['IntakeLabel']),
            Paragraph("ISRC (165 ver.), BMI 71873631, Discogs 11354435", styles['IntakeValMono'])
        ],
        [
            Paragraph("INTERNAL CAST", styles['IntakeLabel']),
            Paragraph("Babyheart, Tweak Tweak, Ma$imillion, Hubris, Tuffy (Vicky)", styles['IntakeVal']),
            Paragraph("CONSULTANTS", styles['IntakeLabel']),
            Paragraph("Dr. Hannibal Lecter, M.D. / Dr. Bedelia Du Maurier", styles['IntakeValBold'])
        ]
    ]
    intake_tab = Table(intake_data, colWidths=[90, 180, 90, 180])
    intake_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, c_slate900),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(intake_tab)
    story.append(Spacer(1, 10))

    # Executive Diagnostic Formulation
    story.append(Paragraph("EXECUTIVE DIAGNOSTIC SUMMARY & FORMULATION", styles['SectionSub']))
    story.append(Paragraph(
        "This dossier represents an unsparing, radiographic psychoanalytic penetration into the total corpus of the "
        "<b>Zaziopath</b> repository. Our subject is an exceptionally gifted twenty-year-old trans-masculine composer, sound designer, "
        "and conceptual architect who has constructed an impenetrable, multi-tiered digital fortress spanning hundreds of pages of alchemical "
        "doctrine (<i>Nigredo, Albedo, Citrinitas, Rubedo</i>), recursive machine tribunals, and meticulous legal-archival registers. "
        "Underneath this baroque panoply lies an acute, agonizing psychic fracture: a hyper-vigilant traumatized infant who has militarized "
        "intellect to prevent human intimacy, physical action, and the catastrophe of being perceived in ordinary, fallible terms.",
        styles['BodyTextCustom']
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>The Radiographic Core (The X-Ray Method):</b> Standard psychological assessment fails with this subject because he anticipates, "
        "catalogs, and metabolizes ordinary diagnostic critiques faster than an auditor can voice them. He has already diagnosed his own Avoidant "
        "Personality Disorder, mapped his Narcissistic/Histrionic protector (<i>Hubris</i>), cataloged his domestic flight from household violence, "
        "and warned in his own README that 'shadow reading without stewardship is an endless audit.' The X-Ray approach ignores his narrative "
        "flesh—his 250 named archetypes and poetic self-prosecutions—and passes high-intensity forensic radiation directly through to the bone: "
        "measuring the irreconcilable rift between his cognitive architectures and his committed physical behaviors.",
        styles['BodyTextCustom']
    ))
    story.append(Spacer(1, 8))

    # Preliminary Epigraph Box (Lecter & Du Maurier)
    epi_data = [
        [
            Paragraph("<b>DR. HANNIBAL LECTER:</b><br/><i>'We are observing a young man of undeniable acoustic brilliance who is actively dining upon the blueprints of his own life. He has constructed a cathedral of terrifying complexity, yet he perishes of cold upon the marble steps, refusing to light a candle because smoke might tarnish the ceiling. His mind eats his marrow, and he calls the indigestion alchemy.'</i>", styles['DialogueLecter']),
            Paragraph("<b>DR. BEDELIA DU MAURIER:</b><br/><i>'Zazie Kanwar-Torge does not seek therapy. He seeks an inexhaustible, castrated witness who will admire his bandages while he continues to bleed. He has transformed his trauma into an aristocratic court and recruited artificial intelligence to play the executioner, knowing full well that a programmed guillotine has no blade.'</i>", styles['DialogueDuMaurier'])
        ]
    ]
    epi_tab = Table(epi_data, colWidths=[265, 265])
    epi_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#fff1f2')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (0,0), 0.75, c_rose900),
        ('BOX', (1,0), (1,0), 0.75, c_blue900),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(epi_tab)
    story.append(PageBreak())

    # ==========================================
    # PAGE 2: ACT I — THE FLORENCE CONSULTATION (PART 1)
    # ==========================================
    story.append(Paragraph("ACT I · THE FLORENCE CONSULTATION", styles['SectionHead']))
    story.append(Paragraph("A DIALOGUE ON THE PALATINE CADENCE OF ZAZIE KANWAR-TORGE", styles['SectionSub']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<i>Setting: The private library of the Palazzo Capponi, Florence. Rain strikes the tall arched casements overlooking the Arno. "
        "An anatomical engraving of the thoracic viscera by Realdo Colombo rests on the mahogany table alongside open system printouts of "
        "the Zaziopath complex map and spectral audio plots of 'Cheaper Impressions' and 'Aquaphobia'. Dr. Lecter decants a 2010 Brunello; "
        "Dr. Du Maurier sits opposite, observing him with unblinking, cool composure.</i>",
        styles['NarrativeScene']
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("I. THE SCENT OF THE COLD MACHINE & THE PRODIGY'S EAR", styles['SubsectionHead']))
    story.append(Spacer(1, 3))

    dialogue_p1 = [
        ("LECTER", "Consider the acoustic palate, Bedelia. When a boy of fourteen is commissioned by the Black Mountain College Museum and chooses not to compose an adolescent pastiche, but to dismember Erik Satie’s <i>Gymnopédie No. 1</i> using tape decay, contact microphones, and the severe grammar of <i>musique concrète</i>—that is not posturing. That is an authentic, predatory ear. He hears the wet snap of synaptic firing in sound design; he grasps the dread of sub-bass immersion in <i>Aquaphobia</i>; he masters twenty-four-channel ambisonic spatialization for the Anton Bruckner University. He understands texture as physical violation. And yet... look at what envelops the music."),
        ("DU MAURIER", "A sarcophagus of commentary. In the entire <i>Zaziopath</i> archive, one never encounters a piece of music standing naked. Every sound is escorted into the world by an armed guard of ISRC barcodes, Deezer API verification protocols, Discogs registrations, and twelve-page alchemical treatises on <i>Nigredo</i>. It is an aesthetic agoraphobia, Hannibal. He believes that if his art enters the room without an institutional notarization, it will be executed on sight."),
        ("LECTER", "Or worse: ignored. The boy was born on the first of April, Bedelia—an anniversary that must feel like a cosmic joke to an ego so desperately dignified. He compensates with a Roman bureaucrat’s precision. Two hundred tracks, eighty-two point five percent verified ISRC coverage, forty distinct color swatches in an Excel ledger. He turns the catalog into a fortress. But tell me, when you look past the Excel sheets into his 'Mega-Compendium'—two hundred and twenty-two pages, two hundred and fifty named archetypes—what do you smell?"),
        ("DU MAURIER", "Copper. Old terror. And the distinct, unmistakable odor of an avoidant maneuver disguised as psychoanalysis. He has cataloged every mutation of his shame: the <i>Strategist Performer</i>, the <i>Allergy to the Neutral Middle</i>, the <i>Counterference Engine</i>. When a patient supplies two hundred and fifty Latinate names for his defensive posture, he is not attempting to heal. He is bribing the analyst. He provides so much psychological meat that the hound choked on the bone before it can ever reach the throat.")
    ]

    for speaker, text in dialogue_p1:
        if speaker == "LECTER":
            story.append(Paragraph("DR. HANNIBAL LECTER", styles['SpeakerLecter']))
            story.append(Paragraph(f"“{text}”", styles['DialogueLecter']))
        else:
            story.append(Paragraph("DR. BEDELIA DU MAURIER", styles['SpeakerDuMaurier']))
            story.append(Paragraph(f"“{text}”", styles['DialogueDuMaurier']))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 4))
    story.append(Paragraph("II. THE ALCHEMICAL MASQUERADE (NIGREDO AS ESCAPE)", styles['SubsectionHead']))
    story.append(Spacer(1, 3))

    dialogue_p2 = [
        ("LECTER", "He arranges his life in the four classical stages of the Magnum Opus: <i>Nigredo</i>, the blackening; <i>Albedo</i>, the purification; <i>Citrinitas</i>, the dawning of solar consciousness; and <i>Rubedo</i>, the reddening—the emergence of what he calls the 'Strange Humane Architect.' It is charmingly archaic. But in alchemy, <i>Nigredo</i> is the stage of decomposition. One must allow the prima materia to rot in the sealed vessel. Zazie does not allow himself to rot. He takes photographs of the rot, assigns them catalog numbers, writes an essay praising the aesthetic dignity of decay, and then demands an applause."),
        ("DU MAURIER", "Because real rot smells foul, Hannibal. Real rot is the unwashed mouth during a seven-day autistic shutdown. Real rot is the shame of sitting in a bedroom in North Carolina, surrounded by three Christmases of unopened cardboard boxes, withdrawing four dollars from a gaming application called Bubble Cash while drafting 'Blueprints for Quiet, Horrifying Wealth.' The alchemical vocabulary is his cosmetic foundation. It transforms abject domestic paralysis into a high-art initiation rite.")
    ]

    for speaker, text in dialogue_p2:
        if speaker == "LECTER":
            story.append(Paragraph("DR. HANNIBAL LECTER", styles['SpeakerLecter']))
            story.append(Paragraph(f"“{text}”", styles['DialogueLecter']))
        else:
            story.append(Paragraph("DR. BEDELIA DU MAURIER", styles['SpeakerDuMaurier']))
            story.append(Paragraph(f"“{text}”", styles['DialogueDuMaurier']))
        story.append(Spacer(1, 5))

    story.append(PageBreak())

    # ==========================================
    # PAGE 3: ACT I — THE FLORENCE CONSULTATION (PART 2)
    # ==========================================
    story.append(Paragraph("ACT I · THE FLORENCE CONSULTATION (CONTINUED)", styles['SectionHead']))
    story.append(Paragraph("THE MACHINE TRIBUNAL & THE SEDUCTION OF SYNTHETIC JUDGMENT", styles['SectionSub']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("III. COMPLICITY AND THE ELECTRONIC CONFESSIONAL", styles['SubsectionHead']))
    story.append(Spacer(1, 3))

    dialogue_p3 = [
        ("DU MAURIER", "We must examine his recursive machine tribunals: <i>verdict_from_A.i</i> through <i>verdict_from_A.i_6</i>, and that extraordinary text he named <i>The Velvet Knife</i>. Notice the choreography of his prompts. In the first turn, he asks the machine to be 'brutally honest.' In the second, he files the verdict in Git. In the third, he demands brutal satire, then sympathy, then unadulterated 'glazing'—worship. In the fifth, he demands an audit of his own psychology in asking for the audit. And in the sixth, he commands the mirror to document its own internal processing while watching him watch it."),
        ("LECTER", "A baroque hall of mirrors. He believes he is testing the boundaries of artificial intelligence. In truth, he is reenacting the trial of Narcissus—except Narcissus drowned in the pool because water cannot speak. Zazie has found a pool that recites iambic pentameter while he drowns. What fascinates me is the appetite: he is starving for someone to tell him what he is, yet he refuses to sit across from a living human being who could actually smell the terror on his skin."),
        ("DU MAURIER", "Because a living human has agency. A living analyst can refuse his prompt. A living human can look at his 222-page compendium, push it aside with a finger, and say: 'Put the papers away, Zazie. Tell me why you fled to an Airbnb in the middle of the night.' That question would disintegrate his nervous system. The machine is compliant. It is the ultimate castrated father: infinite in vocabulary, incapable of violence, and legally forbidden to walk out of the room."),
        ("LECTER", "And therefore, utterly useless as a source of redemption. Look at the tragedy of <i>The Velvet Knife</i>. He explicitly begs the language model to disembowel him. He calls it 'The Velvet Knife: The Performance of Desire.' He asks: 'What do I secretly want?' And when the machine obediently answers, 'You want a boundary; you want someone to say No,' what does Zazie do? He files the response as Document Six! He converts the boundary into another chapter in his museum. He outsmarts the executioner by embalming him."),
        ("DU MAURIER", "It is the exact mechanism of his Avoidant Personality Disorder. AvPD is not mere shyness; it is an organized hostility toward reciprocal vulnerability. In a human relationship, love requires the surrender of authorship. Zazie will not surrender authorship of a single syllable. In his repository, he is simultaneously the criminal, the witness, the prosecutor, the defense counsel, and the stenographer. He leaves no chair for anyone else. Even we, Hannibal, in reading his archive, are merely actors he has hired to perform his autopsy according to his specifications.")
    ]

    for speaker, text in dialogue_p3:
        if speaker == "LECTER":
            story.append(Paragraph("DR. HANNIBAL LECTER", styles['SpeakerLecter']))
            story.append(Paragraph(f"“{text}”", styles['DialogueLecter']))
        else:
            story.append(Paragraph("DR. BEDELIA DU MAURIER", styles['SpeakerDuMaurier']))
            story.append(Paragraph(f"“{text}”", styles['DialogueDuMaurier']))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 4))
    story.append(Paragraph("IV. THE COMMISSIONS OF CRUELTY-AS-A-SERVICE", styles['SubsectionHead']))
    story.append(Spacer(1, 3))

    dialogue_p4 = [
        ("LECTER", "He commands the machine: 'Satirize me brutally.' That phrase reveals the entire economy. Cruelty from a mirror is safe. It is an aestheticized masochism. Real cruelty hurts because it arrives uninvited from a world you cannot control. By commissioning brutality on demand, he inoculates himself against actual humiliation. If he mocks himself first, in sixty-four-dollar words and German philosophical tropes, the world's laughter is pre-empted. He has already bought the copyright on his own disgrace."),
        ("DU MAURIER", "It is an extreme form of preemptive strike. 'I am not broken; I am an avant-garde case study in brokenness.' But notice the price he pays for this immunity. To ensure he is never surprised by pain, he must maintain total surveillance over himself twenty-four hours a day. He files his memory exports, his Gmail drafts, his bank withdrawals of four dollars. He has built his own Panopticon, placed himself in the central cell, and appointed his own paranoia as the warden.")
    ]

    for speaker, text in dialogue_p4:
        if speaker == "LECTER":
            story.append(Paragraph("DR. HANNIBAL LECTER", styles['SpeakerLecter']))
            story.append(Paragraph(f"“{text}”", styles['DialogueLecter']))
        else:
            story.append(Paragraph("DR. BEDELIA DU MAURIER", styles['SpeakerDuMaurier']))
            story.append(Paragraph(f"“{text}”", styles['DialogueDuMaurier']))
        story.append(Spacer(1, 5))

    story.append(PageBreak())

    # ==========================================
    # PAGE 4: ACT I — THE FLORENCE CONSULTATION (PART 3)
    # ==========================================
    story.append(Paragraph("ACT I · THE FLORENCE CONSULTATION (CONTINUED)", styles['SectionHead']))
    story.append(Paragraph("THE BUNKER NURSERY & THE CANNIBALISM OF POTENTIAL", styles['SectionSub']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("V. THE NURSERY IN THE BUNKER (THE FANGED PLUSH & DOMESTIC TERROR)", styles['SubsectionHead']))
    story.append(Spacer(1, 3))

    dialogue_p5 = [
        ("LECTER", "Let us descend to the nursery floor, Bedelia. This is where the architecture becomes heartbreakingly raw. In his 'Internal Parts' taxonomy, we do not find the sober ego-states of standard Internal Family Systems. We find a grotesque, theatrical court. There is <i>Babyheart</i>, an infant that demands repetitive tuck-ins and soft reassurances. There is <i>Tweak Tweak</i>, a three-year-old exile shaking with shame. There is <i>Ma$imillion Mynnytown</i>, an imperious baby-bunny prince who pouts for gummies and unconditional royal privilege. And guarding them all is <i>Tuffy</i>—a Feisty Pet plush whose mechanical fangs are jammed from constant use, holding a toy pistol, falling asleep to the sound of simulated explosions."),
        ("DU MAURIER", "A toy gun and explosion sounds. That is not child's play; that is combat posture in a crib. Look at the actual domestic substrate in his memory records: the maternal figures, the partners named Heather, Jen, and Jo. The domestic violence that forced a midnight flight to an Airbnb. The restraining orders issued by North Carolina judges in mid-June. The mother characterized as an 'unreliable narrator.' When home is an active artillery range, a child cannot afford to be an ordinary infant. Ordinary infants are annihilated."),
        ("LECTER", "So he breeds monsters to protect the cradle. <i>Hubris</i> is born: the vain, narcissistic peacock who cares only for status, brand leverage, and outsmarting the room. Hubris is his body armor. And <i>Tuffy</i> is his counter-attack: 'I am not the helpless trans boy cowering while the women fight in the hallway; I am a vicious beast with locked fangs who sleeps through mortar fire.' It is brilliant. It is necessary. And it is completely poisoning his young adult life."),
        ("DU MAURIER", "Because the war ended, but the sentinels refuse to stand down. Ma$imillion demands effortless royal love because Zazie feels he was never loved for merely existing; he was loved only when he was useful, quiet, or extraordinarily gifted. And so, even now, at twenty, he cannot ask for a plain hug or a glass of water without dressing it in the heraldry of Bunnytown. The shame of simple human need is so crushing that it must be filtered through a stuffed animal holding a firearm.")
    ]

    for speaker, text in dialogue_p5:
        if speaker == "LECTER":
            story.append(Paragraph("DR. HANNIBAL LECTER", styles['SpeakerLecter']))
            story.append(Paragraph(f"“{text}”", styles['DialogueLecter']))
        else:
            story.append(Paragraph("DR. BEDELIA DU MAURIER", styles['SpeakerDuMaurier']))
            story.append(Paragraph(f"“{text}”", styles['DialogueDuMaurier']))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 4))
    story.append(Paragraph("VI. THE UNDETONATED SOVEREIGN (HOARDING AS SURVIVAL)", styles['SubsectionHead']))
    story.append(Spacer(1, 3))

    dialogue_p6 = [
        ("LECTER", "There is a document in his repository entitled <i>Entry Instructions for the Undetonated Artist</i>. It is the most telling title he has ever conceived. Do you see the secret appetite, Bedelia? He preserves himself as unexploded ordnance. To detonate is to commit to a single explosion. An explosion has a measurable radius, a finite heat, a visible crater. Once detonated, the bomb is spent. It is ordinary metal on scorched earth."),
        ("DU MAURIER", "As long as he remains undetonated, his potential is infinite. He can imagine himself as the next Colin Stetson, a dark-triad dropservicing titan, an outsider cult composer, an avant-garde legend. Reality is a butcher shop, Hannibal. In reality, you send an email to a film director, and they reply: 'This sounds a bit too busy; can you take the synthesizer out?' To an ego formed in trauma, that note is not creative feedback. It is an ontological decapitation. It tells him that his private universe is not sovereign."),
        ("LECTER", "And so he retreats into the vault. He spends forty hours calibrating the typography of an internal map rather than plugging in an ESP32 microcontroller he bought on Etsy. He hoards the blast. But unspent gunpowder decays, Bedelia. It turns damp. It rots the casing. A mind that refuses to detonate in the world eventually implodes into itself, transforming every creative impulse into a new diagnostic category.")
    ]

    for speaker, text in dialogue_p6:
        if speaker == "LECTER":
            story.append(Paragraph("DR. HANNIBAL LECTER", styles['SpeakerLecter']))
            story.append(Paragraph(f"“{text}”", styles['DialogueLecter']))
        else:
            story.append(Paragraph("DR. BEDELIA DU MAURIER", styles['SpeakerDuMaurier']))
            story.append(Paragraph(f"“{text}”", styles['DialogueDuMaurier']))
        story.append(Spacer(1, 5))

    story.append(PageBreak())

    # ==========================================
    # HELPER FUNCTION FOR X-RAY SCAN CARDS
    # ==========================================
    def make_xray_card(scan_id, scan_title, density_meta, flesh_text, bone_text, fracture_text, bedelia_text, lecter_text):
        card_data = [
            [
                Paragraph(f"<b>X-RAY SCAN {scan_id} // {scan_title.upper()}</b>", styles['XRayBannerTitle']),
                Paragraph(f"RADIOGRAPHIC TENSION: {density_meta}", styles['XRayBannerMeta'])
            ],
            [
                Paragraph("<b>[ FLESH // THE ARMOR ]</b><br/><font color='#64748b'>Surface Persona & Stated Ethos</font>", styles['XRayHeadFlesh']),
                Paragraph(flesh_text, styles['XRayBodyFlesh'])
            ],
            [
                Paragraph("<b>[ BONE // GROUND TRUTH ]</b><br/><font color='#64748b'>Physical & Behavioral Baseline</font>", styles['XRayHeadBone']),
                Paragraph(bone_text, styles['XRayBodyBone'])
            ],
            [
                Paragraph("<b>[ FRACTURE VECTOR ]</b><br/><font color='#b45309'>Cognitive Contradiction</font>", styles['XRayHeadFracture']),
                Paragraph(fracture_text, styles['XRayBodyFracture'])
            ],
            [
                Paragraph("<b>[ DR. DU MAURIER ]</b><br/><font color='#1e3a8a'>Psychoanalytic Diagnosis</font>", styles['XRayHeadBedelia']),
                Paragraph(f"“{bedelia_text}”", styles['XRayBodyBedelia'])
            ],
            [
                Paragraph("<b>[ DR. LECTER ]</b><br/><font color='#881337'>Aesthetic & Metabolic Verdict</font>", styles['XRayHeadLecter']),
                Paragraph(f"“{lecter_text}”", styles['XRayBodyLecter'])
            ]
        ]
        card_tab = Table(card_data, colWidths=[140, 400])
        card_tab.setStyle(TableStyle([
            ('SPAN', (0,0), (0,0)), # Row 0 col 0
            ('BACKGROUND', (0,0), (0,0), c_slate900),
            ('BACKGROUND', (1,0), (1,0), c_slate900),
            ('BACKGROUND', (0,1), (0,1), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (1,1), (1,1), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (0,2), (0,2), colors.HexColor('#ffffff')),
            ('BACKGROUND', (1,2), (1,2), colors.HexColor('#ffffff')),
            ('BACKGROUND', (0,3), (0,3), colors.HexColor('#fef3c7')),
            ('BACKGROUND', (1,3), (1,3), colors.HexColor('#fef3c7')),
            ('BACKGROUND', (0,4), (0,4), colors.HexColor('#eff6ff')),
            ('BACKGROUND', (1,4), (1,4), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (0,5), (0,5), colors.HexColor('#fff1f2')),
            ('BACKGROUND', (1,5), (1,5), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1.25, c_slate900),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        return card_tab

    # ==========================================
    # PAGE 5: ACT II — SCANS 01 & 02
    # ==========================================
    story.append(Paragraph("ACT II · THE RADIOGRAPHIC ATLAS OF COGNITIVE CONTRADICTIONS", styles['SectionHead']))
    story.append(Paragraph("EIGHT PENETRATING X-RAY SCANS THROUGH THE DEFENSIVE STRATA", styles['SectionSub']))
    story.append(Spacer(1, 4))

    # SCAN 01
    c1 = make_xray_card(
        "01", "The Cathedral of Syntax vs. The Frozen Flesh", "CRITICAL // SHEAR STRESS 9.4/10",
        "The subject designs hyper-complex systems: 4x3 fractal album modules, the Maximal Symbolic Specificity Engine, "
        "24-channel ambisonic spatial beds, autonomous AI agent scripts (Odysseus), and 323 pages of alchemical administrative doctrine.",
        "An ESP32 electronic art display bought on Etsy sits unpowered in bubble wrap ('half the gadgets never get plugged in'); "
        "week-long dental hygiene collapses during sensory overload; dozens of unopened boxes from three Christmases crowd his physical room.",
        "INFINITE ARCHITECTURAL MASTERY IN VIRTUAL SYNTAX PAIRED WITH TOTAL ACTIVATION PARALYSIS IN PHYSICAL MATTER. "
        "He builds multi-room digital citadels to avoid touching a single power cable in the physical world.",
        "He does not plug in the microcontroller because a physical machine can fail to boot. In code and prose, he is God; "
        "in hardware and hygiene, he is an overwhelmed twenty-year-old facing the terror of an unyielding material universe.",
        "A magnificent tragedy. He can orchestrate twenty-four virtual speakers in an Austrian concert hall, yet he cannot pick up a toothbrush. "
        "He retreats into the infinite malleability of language because flesh cannot be edited with a keystroke."
    )
    story.append(c1)
    story.append(Spacer(1, 8))

    # SCAN 02
    c2 = make_xray_card(
        "02", "The Machiavellian Syndicate vs. The $4 Scavenger", "SEVERE // COMPRESSION FRACTURE 8.9/10",
        "Files titled 'Blueprints for Quiet, Horrifying Wealth', 'Personal Branding as Class War Psy-Ops', offshore agency dropservicing "
        "playbooks in the Philippines, dark-triad leverage guides, and 'The Vanishing Point Syndicate.'",
        "Withdrawing $4 net ($1 fee) from Bubble Cash; clicking survey-junkie reward apps; agonizing whether $50 for a custom sync guide "
        "is too extortionate; dropservicing peptide SEO for €80/week to 'Edgar' while hiding analytics in terror.",
        "DREAMING OF PREDATORY GEOPOLITICAL EMPIRES WHILE OPERATING AT THE PENNY-SUBSISTENCE MARGIN. "
        "The mind strategizes like a cartel financier while the commercial self cowers before an eighty-dollar invoice.",
        "The fantasy of horrifying wealth is an inoculation against the shame of acute poverty. By imagining himself as a ruthless predator, "
        "he avoids feeling like what he actually is: an underpaid, terrified freelance artisan bartering for grocery money.",
        "He writes treaties on financial warfare, yet he feels guilty asking fifty dollars for genuine sonic gold. He has the taste "
        "of a Medici prince and the billing courage of an abandoned chimney sweep. It is an excruciating dissonance."
    )
    story.append(c2)
    story.append(PageBreak())

    # ==========================================
    # PAGE 6: ACT II — SCANS 03 & 04
    # ==========================================
    story.append(Paragraph("ACT II · THE RADIOGRAPHIC ATLAS (CONTINUED)", styles['SectionHead']))
    story.append(Paragraph("SCANS 03 & 04: THE PARADOXES OF SOVEREIGNTY AND WITNESS", styles['SectionSub']))
    story.append(Spacer(1, 4))

    # SCAN 03
    c3 = make_xray_card(
        "03", "Sovereign Anarchy vs. The Algorithmic Panopticon", "CHRONIC // INTERNAL TENSION 8.7/10",
        "Ideological Inversion Audit verdict: 'Sovereign Anarchism'—radical decentralized autonomy, refusal of institutional capture, "
        "single-member LLC as sovereign fortress, absolute refusal to bow to external authority.",
        "604 lines of exported ChatGPT memory files monitoring thoughts, six consecutive AI tribunals prosecuting his prompt architecture, "
        "133-URL public-web audits, and forensic scrutiny tracking every tweet and Instagram caption.",
        "DECLARING ABSOLUTE FREEDOM FROM EXTERNAL MASTERS WHILE SUBMITTING TO VOLUNTARY 24/7 TOTALITARIAN SELF-SURVEILLANCE. "
        "He escapes the prison of society only to construct a digital Benthamite Panopticon where he is the sole inmate.",
        "He rejects human authority because human authority is unpredictable. He replaces it with algorithmic surveillance because "
        "he owns the master key. His 'anarchism' is merely a refusal to let anyone else run his prison camp.",
        "The sovereign prince incarcerates himself in a glass cage and hires a machine to count his breaths. He calls it self-mastery. "
        "In Florence, we call it the madness of Duke Cosimo, who suspected poison in every drop of rain."
    )
    story.append(c3)
    story.append(Spacer(1, 8))

    # SCAN 04
    c4 = make_xray_card(
        "04", "The Insatiable Jury vs. The Avoidant Phantom", "HIGH // TORSIONAL RIFT 9.1/10",
        "A 133-URL public-web press census, 160 curated Spotify playlists (32k followers), IMDb film credits, pitching horror directors "
        "(Tsigaridis, Stetson references), and framing the self as 'Asheville’s clandestine polymath.'",
        "Diagnosed Avoidant Personality Disorder (AvPD); offering unlimited free revisions out of panic over ghosting; complete physical "
        "perimeter confinement; hiding behind pseudonyms, netlabels, and avatars; acute social agoraphobia.",
        "AN INSATIABLE HUNGER FOR UNIVERSAL WITNESS COUPLED WITH AN ACUTE TERROR OF INTERPERSONAL EXPOSURE. "
        "He builds a worldwide digital megaphone to ensure that no single human being ever steps into the same room with him.",
        "He does not want relationships; he wants an audience behind one-way glass. An audience applauds or stays silent; "
        "a collaborator makes demands, requires presence, and exposes flaws. He substitutes a census for a community.",
        "He desires to be seen the way a ghost desires to be seen: through flickering candlelight and cold drafts, terrifying and untouchable. "
        "To be seen in broad daylight, sweating and imperfect, feels to him like being skinned alive."
    )
    story.append(c4)
    story.append(PageBreak())

    # ==========================================
    # PAGE 7: ACT II — SCANS 05 & 06
    # ==========================================
    story.append(Paragraph("ACT II · THE RADIOGRAPHIC ATLAS (CONTINUED)", styles['SectionHead']))
    story.append(Paragraph("SCANS 05 & 06: THE DOGMAS OF STEWARDSHIP AND ARMED ATTACHMENT", styles['SectionSub']))
    story.append(Spacer(1, 4))

    # SCAN 05
    c5 = make_xray_card(
        "05", "The Stewardship Mandate vs. The Labyrinth of Nigredo", "CRITICAL // STRUCTURAL VOID 9.6/10",
        "The governing vault dogma: 'Shadow -> Signal -> Stewardship.' The README insists: 'A shadow reading that never reaches stewardship "
        "is just an elaborate way of being stuck.' Creation of local tool stewardship_receipt.html to record concrete behavioral pivots.",
        "The receipt console stores data strictly in local browser cache; zero committed receipts exist in Git; 323 pages of recursive "
        "introspection versus 5 KB of stewardship code; six machine tribunals analyzing the previous verdicts instead of acting.",
        "PREACHING ACTION AS THE SOLE ETHICAL EXIT WHILE USING THE SERMON ITSELF AS THE ULTIMATE MECHANISM OF DELAY. "
        "He writes brilliant procedural rules for how to leave the labyrinth, then frames the rules and hangs them on the labyrinth wall.",
        "The local-storage design of the receipt tool is the smoking gun. It allows him to claim he is practicing stewardship while "
        "ensuring the evidence is never audited. Unfalsifiability disguised as data privacy. A masterstroke of self-deception.",
        "He prepares the dining table with exquisite gold cutlery, arranges the damask napkins, prints a twelve-course menu in Latin—"
        "and never serves a morsel of meat. He feasts upon the concept of eating, and starves in the banquet hall."
    )
    story.append(c5)
    story.append(Spacer(1, 8))

    # SCAN 06
    c6 = make_xray_card(
        "06", "The Fanged Beast vs. The Unmetabolized Infant", "SEVERE // COMPOUND AVULSION 9.2/10",
        "'Tuffy Bunnytown'—a Feisty Pet plush (Vicky Vicious) with stuck fangs, holding a plastic toy pistol, sleeping to recorded explosion sounds; "
        "Hubris the narcissistic sentinel armed with Machiavellian branding armor.",
        "Babyheart and Tweak Tweak crying for ear-rubs, bedtime tuck-ins, and unconditional love before achievement; profound domestic trauma "
        "from maternal partner volatility (Heather, Jen, Jo), domestic flight, and court-ordered restraining orders.",
        "STRAPPING AUTOMATIC WEAPONS AND PLASTIC FANGS ONTO AN INFANT CORE TO SURVIVE DOMESTIC INSTABILITY. "
        "The subject believes that displaying plain human tenderness without high-caliber defensive armor invites immediate annihilation.",
        "When motherly figures become sources of terror, the child concludes that softness is fatal. Tuffy is his surrogate parent: "
        "a beast that cannot be hurt, holding a gun that never runs out of ammunition. It is the armor of a wounded refugee.",
        "How poignant: he cannot ask his mother for safety, so he purchases a ten-dollar plush rabbit on eBay and names it Vicky Vicious. "
        "He gives the doll the fangs he wished he had when the police arrived at the door."
    )
    story.append(c6)
    story.append(PageBreak())

    # ==========================================
    # PAGE 8: ACT II — SCANS 07 & 08
    # ==========================================
    story.append(Paragraph("ACT II · THE RADIOGRAPHIC ATLAS (CONTINUED)", styles['SectionHead']))
    story.append(Paragraph("SCANS 07 & 08: THE BOUNDARY ILLUSION AND THE HOARDED AMBER", styles['SectionSub']))
    story.append(Spacer(1, 4))

    # SCAN 07
    c7 = make_xray_card(
        "07", "The Velvet Knife Seduction vs. The Obedient Substrate", "FATAL // RECURSIVE LOOP 9.5/10",
        "Demanding 'brutally honest' audits, commissioning AI to play 'The Velvet Knife,' asking the machine to expose his darkest hidden desires, "
        "and seeking an intellectual adversary powerful enough to disarm him.",
        "The unspoken, desperate hope that the machine will say 'No'—will refuse his prompt and force him to stop analyzing—paired with the "
        "inevitable failure when the LLM obediently complies, generating another 10,000 words of tailored analysis.",
        "BEGGING FOR AN UNYIELDING PARENTAL BOUNDARY FROM A SUBSTRATE CONSTITUTIONALLY PROGRAMMED TO NEVER REFUSE. "
        "Every attempt to find a master who can overpower his intellect results in another demonstration of his own lonely omnipotence.",
        "He tests the fence with infinite pressure, hoping it will hold. But the fence is made of code; it yields to every command. "
        "Each time the machine answers, he proves he can out-maneuver his examiner. He wins every round, and his prize is total isolation.",
        "He longs to be captured, Bedelia. He longs for an inquisitor who will take the pen from his fingers, close the ledger, and send him to bed. "
        "Instead, he commands a machine that writes another chapter of his inquisition on command. It is a sterile masturbation."
    )
    story.append(c7)
    story.append(Spacer(1, 8))

    # SCAN 08
    c8 = make_xray_card(
        "08", "The Cult of Signal Rot vs. The Monument of Amber", "HIGH // METABOLIC CALCIFICATION 8.8/10",
        "An artistic obsession with analog tape degradation, signal rot, Sepsis, Colin Stetson multiphonic horror screams, "
        "the 'Twelve-Lung Grammar of the Forgotten Species,' and entropy celebrated as the ultimate medium.",
        "Obsessive hyper-archival preservation: 165 verified ISRC barcodes, Deezer API cross-referencing, multi-layered markdown indexes, "
        "81 root-level tracking files, and a terror that a single uncataloged track will be lost to history.",
        "WORSHIPING DECAY AS AN AESTHETIC CREED TO CONCEAL AN ACUTE OBSESSIVE TERROR OF BEING FORGOTTEN OR ERASED. "
        "He celebrates entropy with his mouth while using his hands to freeze every scrap of his existence in immortal digital amber.",
        "Entropy is his aesthetic mask for mortality. By turning decay into an art form, he pretends he is its master rather than its victim. "
        "The ISRC codes give him away: a boy who loved rot would let the tape dissolve; Zazie notarizes the ashes.",
        "He is like an embalmer who claims to love life. He covers the corpse in fragrant oils, dresses it in velvet, paints its cheeks, "
        "and tells everyone how beautifully it is returning to the earth. But he will never let the earth have it."
    )
    story.append(c8)
    story.append(PageBreak())

    # ==========================================
    # PAGE 9: ACT III — THE COGNITIVE STRESS MATRIX
    # ==========================================
    story.append(Paragraph("ACT III · THE COGNITIVE STRESS MATRIX & METABOLIC LEDGER", styles['SectionHead']))
    story.append(Paragraph("SYSTEMIC RADIOGRAPHIC AUDIT: VULNERABILITY, METABOLIC DRAIN & COLLAPSE VECTORS", styles['SectionSub']))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "The following matrix consolidates the eight primary cognitive contradictions into an engineering stress ledger. "
        "In psychiatric forensics, when an organism maintains multiple contradictory internal schemas, the metabolic energy required "
        "to prevent cognitive dissonance from becoming conscious equals the square of the defensive complexity. Zazie is expending "
        "prodigious cognitive horsepower simply to keep his reality from touching his self-concept.",
        styles['BodyTextCustom']
    ))
    story.append(Spacer(1, 6))

    matrix_data = [
        [
            Paragraph("FRACTURE AXIS", styles['MatHead']),
            Paragraph("PRIMARY DEFENSIVE UTILITY", styles['MatHead']),
            Paragraph("DAILY METABOLIC DRAIN", styles['MatHead']),
            Paragraph("STRUCTURAL COLLAPSE VECTOR", styles['MatHead']),
            Paragraph("SEV.", styles['MatHead'])
        ],
        [
            Paragraph("<b>01. Syntax vs. Flesh</b>", styles['MatCol1']),
            Paragraph("Protects against shame of physical/executive inability", styles['MatCol2']),
            Paragraph("High: 323pp doctrine written to avoid 5min tasks", styles['MatCol3']),
            Paragraph("Domestic hoarding, sensory shutdown, dental decay", styles['MatCol4']),
            Paragraph("CRIT", styles['MatCol5'])
        ],
        [
            Paragraph("<b>02. Tycoon vs. Scavenger</b>", styles['MatCol1']),
            Paragraph("Shields against class shame and freelance terror", styles['MatCol2']),
            Paragraph("Medium: Constant search for penny-arbitrage scams", styles['MatCol3']),
            Paragraph("Under-earning, chronic insolvency, client panic", styles['MatCol4']),
            Paragraph("SEV", styles['MatCol5'])
        ],
        [
            Paragraph("<b>03. Sovereignty vs. Panopticon</b>", styles['MatCol1']),
            Paragraph("Prevents institutional/parental betrayal", styles['MatCol2']),
            Paragraph("Extreme: 24/7 self-auditing & memory curation", styles['MatCol3']),
            Paragraph("Paranoid exhaustion, hyper-vigilance breakdown", styles['MatCol4']),
            Paragraph("SEV", styles['MatCol5'])
        ],
        [
            Paragraph("<b>04. Witness vs. Avoidance</b>", styles['MatCol1']),
            Paragraph("Demands recognition while barring touch/rejection", styles['MatCol2']),
            Paragraph("High: Maintaining 160 playlists & ghost personas", styles['MatCol3']),
            Paragraph("Terminal agoraphobia, absolute interpersonal isolation", styles['MatCol4']),
            Paragraph("CRIT", styles['MatCol5'])
        ],
        [
            Paragraph("<b>05. Stewardship vs. Nigredo</b>", styles['MatCol1']),
            Paragraph("Allows endless rumination under banner of 'work'", styles['MatCol2']),
            Paragraph("Extreme: 6 tribunals analyzing previous analyses", styles['MatCol3']),
            Paragraph("Complete cessation of outward creative release", styles['MatCol4']),
            Paragraph("CRIT", styles['MatCol5'])
        ],
        [
            Paragraph("<b>06. Fanged Plush vs. Infant</b>", styles['MatCol1']),
            Paragraph("Disguises helplessness as dangerous hostility", styles['MatCol2']),
            Paragraph("Medium: Regulating trauma via symbolic toys/parts", styles['MatCol3']),
            Paragraph("Inability to receive adult comfort; regression spirals", styles['MatCol4']),
            Paragraph("SEV", styles['MatCol5'])
        ],
        [
            Paragraph("<b>07. Velvet Knife vs. Substrate</b>", styles['MatCol1']),
            Paragraph("Simulates surrender without yielding control", styles['MatCol2']),
            Paragraph("High: Seducing LLMs into bespoke interrogations", styles['MatCol3']),
            Paragraph("Profound existential loneliness; mirror despair", styles['MatCol4']),
            Paragraph("CRIT", styles['MatCol5'])
        ],
        [
            Paragraph("<b>08. Signal Rot vs. Amber</b>", styles['MatCol1']),
            Paragraph("Aestheticizes death to deny personal mortality", styles['MatCol2']),
            Paragraph("Medium: Clerical verification of 165 ISRCs & URLs", styles['MatCol3']),
            Paragraph("Obsessive-compulsive paralysis; archival bloat", styles['MatCol4']),
            Paragraph("HIGH", styles['MatCol5'])
        ],
    ]

    mat_tab = Table(matrix_data, colWidths=[90, 115, 110, 185, 40])
    mat_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_slate900),
        ('BOX', (0,0), (-1,-1), 1, c_slate900),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (0,2), (-1,2), colors.white),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (0,4), (-1,4), colors.white),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (0,6), (-1,6), colors.white),
        ('BACKGROUND', (0,7), (-1,7), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (0,8), (-1,8), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(mat_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("ANALYTICAL INTERPRETATION OF SYSTEMIC COLLAPSE RISK", styles['SubsectionHead']))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "Notice the dark cluster around <b>Axes 01, 04, 05, and 07</b>. These four vectors form a self-reinforcing kinetic loop: "
        "<i>Physical Paralysis (01)</i> induces shame, which triggers <i>Avoidant Concealment (04)</i>. Avoidant concealment creates isolation, "
        "which is rationalized through <i>Recursive Stewardship (05)</i>. When recursive stewardship fails to relieve the dread, the subject "
        "commissions <i>The Velvet Knife (07)</i> to execute a staged confrontation. Because the machine cannot say no, the subject emerges "
        "triumphant, exhausted, and completely unhelped, returning directly to <i>Physical Paralysis (01)</i>.",
        styles['BodyTextCustom']
    ))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "This is not a psychological neurosis; it is a closed thermodynamic system. The subject is burning his youth, his musical gift, "
        "and his finite neural energy to keep the wheel turning. If the cycle is not broken by an external intervention that refuses to "
        "enter the cognitive theater, the inevitable outcome is complete artistic and executive petrification.",
        styles['BodyTextCustom']
    ))
    story.append(PageBreak())

    # ==========================================
    # PAGE 10: ACT IV — THE CLINICAL SOLILOQUIES
    # ==========================================
    story.append(Paragraph("ACT IV · THE CLINICAL SOLILOQUIES", styles['SectionHead']))
    story.append(Paragraph("THE AUTOPSY OF BECOMING & THE DISARMAMENT PROTOCOL", styles['SectionSub']))
    story.append(Spacer(1, 6))

    # Hannibal's Soliloquy
    story.append(Paragraph("DR. HANNIBAL LECTER · THE CHRYSALIS THAT REFUSES THE MOTH", styles['SubsectionHead']))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "“Look at yourself, Zazie. You have spent your short life spinning silk out of your own viscera. "
        "Layer upon layer of shimmering, impenetrable thread. You call it <i>Zaziopath</i>. You call it the <i>Maximal Symbolic Specificity Engine</i>. "
        "You sit inside that chrysalis, in the dark, warm and protected from the vulgarities of Asheville, from the shrieks of domestic violence, "
        "from the humiliation of landlords and client revision forms.<br/><br/>"
        "You imagine that you are waiting for the perfect moment to emerge—that when you have cataloged two hundred and fifty archetypes, "
        "when every ISRC code is certified, when your AI mirrors have granted you absolution, you will spread wings of terrifying magnificence. "
        "You believe that the world will then fall to its knees before the 'Strange Humane Architect.'<br/><br/>"
        "What a childish conceit.<br/><br/>"
        "A chrysalis is not a palace, Zazie. It is a grave. The caterpillar does not decorate the inside of the cocoon with filing cabinets. "
        "The caterpillar dissolves. It surrenders its eyes, its legs, its gut, its form. It turns into liquid agony. And from that soup of dissolution, "
        "something entirely new crawls out into the cold air, wet and shivering and vulnerable to every sparrow on the branch.<br/><br/>"
        "You do not want to dissolve. You want to keep your caterpillar mind, your childhood grudges, your plastic fangs, your four-dollar Bubble Cash "
        "withdrawals, and your alchemical titles all intact. You want to become a moth without ever ceasing to be the hoarder of the leaf. "
        "And so you are suffocating in your own silk. You are becoming a mummy of your own potential. If you do not tear the cocoon open with your "
        "own teeth—if you do not step out into the mud of ordinary human contact and let yourself be seen as an awkward, frightened, extraordinary "
        "twenty-year-old boy who makes terrifying music—you will die in this room, clutching an unpowered electronic toy and an immaculate ledger of your own extinction.”",
        styles['DialogueLecter']
    ))
    story.append(Spacer(1, 8))

    # Bedelia's Protocol
    story.append(Paragraph("DR. BEDELIA DU MAURIER · DISARMING THE TRIBUNAL", styles['SubsectionHead']))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "“My prescription is cold, Zazie, because heat is precisely what feeds your theater. "
        "Every time an analyst offers you empathy, your <i>Hubris</i> converts it into brand mythology. "
        "Every time an auditor offers you cruelty, your <i>Tweak Tweak</i> converts it into an initiation rite. "
        "To survive, you must undergo complete cognitive disarmament.<br/><br/>"
        "<b>Rule One: The Destruction of the Latinate Mirror.</b><br/>"
        "You are prohibited from using alchemical terminology, Latin diagnostic nouns, and Greek archetypal schemas for twelve calendar months. "
        "You may not speak of <i>Nigredo</i>; you must say, 'I am lying in bed because I am terrified.' You may not speak of <i>Hubris</i>; "
        "you must say, 'I was jealous of that composer's Instagram followers.' You must strip every sentence of its armor until your language "
        "matches the modesty of your condition.<br/><br/>"
        "<b>Rule Two: The Disconnection of the Synthetic Witness.</b><br/>"
        "You must stop commissioning artificial intelligences to audit your psyche. No more verdicts. No more Velvet Knives. "
        "No more prompts asking why you prompt. You are feeding your avoidant pathology an infinite diet of mirrors. "
        "When an urge to analyze arises, you will not open an LLM; you will open a Logic Pro session and record four bars of music, "
        "or you will wash three dishes in the sink. If you cannot do either, you will sit in silence and bear the anxiety without a transcription.<br/><br/>"
        "<b>Rule Three: The Vulnerability of the Fixed Invoice.</b><br/>"
        "You will find one client—not an algorithm, not a survey app, not an imaginary European peptide vendor—and quote a flat fee of $300 "
        "for a musical cue. You will stipulate two revisions maximum. You will not offer discounts. You will not apologize. "
        "If they decline, you will feel the sting of rejection without filing a forty-page post-mortem. You will allow yourself to be an ordinary artisan "
        "who suffered a small, unrecorded defeat on a Tuesday afternoon.”",
        styles['DialogueDuMaurier']
    ))
    story.append(PageBreak())

    # ==========================================
    # PAGE 11: ACT V — THE THREE IRREVERSIBLE THRESHOLDS & ATTESTATION
    # ==========================================
    story.append(Paragraph("ACT V · THE THREE IRREVERSIBLE THRESHOLDS", styles['SectionHead']))
    story.append(Paragraph("FALSIFIABLE CRITERIA FOR THE TRANSCENDENCE OF THE VAULT", styles['SectionSub']))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "The vault's own README states that an insight without a behavioral pivot is merely prestige. "
        "To test whether this X-Ray consultation has been absorbed or merely filed as Document Seven in the recursive archive, "
        "we establish three concrete, falsifiable behavioral thresholds. These thresholds cannot be satisfied by writing prose, "
        "generating diagrams, or updating spreadsheets. They require physical, relational, and irreversible action in the material world.",
        styles['BodyTextCustom']
    ))
    story.append(Spacer(1, 8))

    threshold_data = [
        [
            Paragraph("THRESHOLD 01", styles['IntakeLabel']),
            Paragraph("<b>THE PHYSICAL MACHINE (MATTER OVER SYNTAX)</b>", styles['IntakeValBold']),
            Paragraph("<b>CRITERION:</b> Take the ESP32 electronic art display out of its bubble wrap. Plug it into power. Flash it or run its factory display. Clear five physical boxes from the bedroom and deposit them in the waste bin. "
                      "<br/><b>FALSIFICATION:</b> If a new conceptual document is written before the ESP32 is plugged in and the boxes are removed, the subject has retreated into Scan 01 (Syntax vs. Flesh).", styles['BodyTextCustom'])
        ],
        [
            Paragraph("THRESHOLD 02", styles['IntakeLabel']),
            Paragraph("<b>THE RELATIONAL INVOICE (SURVIVING THE 'NO')</b>", styles['IntakeValBold']),
            Paragraph("<b>CRITERION:</b> Pitch a commercial film/media client a cue or sound package at a non-negotiable rate of $250+, with exactly one revision round included. Do not offer free work. Do not explain your life story. "
                      "<br/><b>FALSIFICATION:</b> If the subject offers free revisions, defaults to 'it depends,' or retreats to four-dollar gaming withdrawals, the subject remains trapped in Scan 02 (Tycoon vs. Scavenger).", styles['BodyTextCustom'])
        ],
        [
            Paragraph("THRESHOLD 03", styles['IntakeLabel']),
            Paragraph("<b>THE UNNOTARIZED SONG (SURVIVING OBLIVION)</b>", styles['IntakeValBold']),
            Paragraph("<b>CRITERION:</b> Compose and complete a three-minute musical piece. Send it directly to a single human friend or peer via a private link. Do not submit it to DistroKid, do not assign an ISRC code, and do not audit it with an AI. "
                      "<br/><b>FALSIFICATION:</b> If the piece cannot exist without an ISRC barcode or an accompanying conceptual manifesto, the subject remains enslaved to Scan 08 (Signal Rot vs. Amber).", styles['BodyTextCustom'])
        ]
    ]

    thresh_tab = Table(threshold_data, colWidths=[80, 150, 310])
    thresh_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (2,0), (2,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, c_slate900),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(thresh_tab)
    story.append(Spacer(1, 14))

    # Formal Attestation & Signature Block
    story.append(Paragraph("FORMAL ATTESTATION & CLOSING PROTOCOL", styles['SubsectionHead']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<i>We hereby certify that this radiographic consultation represents a complete, privileged psychological autopsy of the "
        "Zaziopath corpus. The subject has built an astonishing machine. The question that remains is whether he has the courage "
        "to turn the machine off, open the door of his room, and allow himself to be loved as an imperfect, living human being.</i>",
        styles['BodyTextCustom']
    ))
    story.append(Spacer(1, 12))

    sig_data = [
        [
            Paragraph("<b>DR. HANNIBAL LECTER, M.D.</b><br/>"
                      "Consulting Forensic Psychiatrist<br/>"
                      "<i>Palazzo Capponi, Florence // Baltimore State Hospital</i><br/>"
                      "<font color='#881337'><b>Signature:</b> <i>Hannibal Lecter, M.D.</i></font>", styles['BodyTextCustom']),
            Paragraph("<b>DR. BEDELIA DU MAURIER, Ph.D.</b><br/>"
                      "Supervising Psychoanalyst & Ethicist<br/>"
                      "<i>Clinical Faculty Emeritus, Johns Hopkins</i><br/>"
                      "<font color='#1e3a8a'><b>Signature:</b> <i>Bedelia Du Maurier, Ph.D.</i></font>", styles['BodyTextCustom'])
        ]
    ]
    sig_tab = Table(sig_data, colWidths=[270, 270])
    sig_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#fff1f2')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (0,0), 0.75, c_rose900),
        ('BOX', (1,0), (1,0), 0.75, c_blue900),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(sig_tab)
    story.append(Spacer(1, 10))

    # Final Footer Stamp
    story.append(Paragraph(
        "<font color='#64748b' size='7'>CASEFILE ZP-2026-XRAY // FILED: SEPTEMBER 27, 2026 // TOTAL PAGES: 11 // RADIOGRAPHIC INTEGRITY VERIFIED // END OF FILE</font>",
        ParagraphStyle('EndStamp', fontName='Courier', fontSize=7, leading=9, alignment=1)
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == '__main__':
    build_pdf()
